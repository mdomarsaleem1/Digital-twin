"""Debate phase implementations."""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import structlog

from agentic_council.agents.base_agent import BaseAgent, AgentResponse, AgentVote
from agentic_council.agents.devils_advocate import DevilsAdvocateAgent
from agentic_council.orchestration.time_manager import TimeManager
from agentic_council.orchestration.voting import VotingSystem

logger = structlog.get_logger()


@dataclass
class PhaseResult:
    """Result from a debate phase."""
    phase_name: str
    duration_seconds: float
    agent_responses: list[AgentResponse]
    votes: list[AgentVote]
    key_disagreements: list[str] = field(default_factory=list)
    phase_summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class DebatePhase(ABC):
    """Abstract base class for debate phases."""

    def __init__(
        self,
        name: str,
        time_manager: TimeManager,
        voting_system: VotingSystem,
    ):
        self.name = name
        self.time_manager = time_manager
        self.voting_system = voting_system

    @abstractmethod
    async def execute(
        self,
        idea: str,
        agents: dict[str, BaseAgent],
        context: dict[str, Any] | None = None,
        previous_results: list[PhaseResult] | None = None,
    ) -> PhaseResult:
        """Execute this phase.

        Args:
            idea: The business idea being evaluated
            agents: Dictionary of available agents
            context: Additional context for the phase
            previous_results: Results from previous phases

        Returns:
            PhaseResult with outcomes
        """
        pass


class ParallelAssessmentPhase(DebatePhase):
    """Phase 1: All agents analyze independently in parallel."""

    def __init__(
        self,
        time_manager: TimeManager,
        voting_system: VotingSystem,
    ):
        super().__init__("parallel_assessment", time_manager, voting_system)

    async def execute(
        self,
        idea: str,
        agents: dict[str, BaseAgent],
        context: dict[str, Any] | None = None,
        previous_results: list[PhaseResult] | None = None,
    ) -> PhaseResult:
        """Execute parallel assessment phase.

        All specialist agents analyze the idea simultaneously without
        seeing each other's responses.
        """
        self.time_manager.start_phase(self.name)
        logger.info("Starting parallel assessment phase", agent_count=len(agents))

        # Filter out devil's advocate - they don't participate in Phase 1
        specialist_agents = {
            k: v for k, v in agents.items()
            if not isinstance(v, DevilsAdvocateAgent)
        }

        # Run all analyses in parallel
        tasks = [
            agent.analyze(idea, context)
            for agent in specialist_agents.values()
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        valid_responses: list[AgentResponse] = []
        votes: list[AgentVote] = []

        for response, agent_id in zip(responses, specialist_agents.keys()):
            if isinstance(response, Exception):
                logger.error(
                    "Agent analysis failed",
                    agent=agent_id,
                    error=str(response),
                )
                continue

            valid_responses.append(response)
            if response.vote:
                votes.append(response.vote)

        duration = self.time_manager.end_phase()

        # Generate phase summary
        aggregation = self.voting_system.aggregate_votes(votes)
        summary = self._generate_summary(votes, aggregation)

        logger.info(
            "Parallel assessment complete",
            responses=len(valid_responses),
            duration_seconds=duration,
        )

        return PhaseResult(
            phase_name=self.name,
            duration_seconds=duration,
            agent_responses=valid_responses,
            votes=votes,
            phase_summary=summary,
            metadata={"aggregation": aggregation},
        )

    def _generate_summary(self, votes: list[AgentVote], aggregation) -> str:
        """Generate a summary of the parallel assessment."""
        if not votes:
            return "No valid assessments received."

        lines = [
            f"Phase 1 Complete: {len(votes)} specialist assessments",
            f"Average Score: {aggregation.average_score:.1f}/10",
            f"Consensus Level: {aggregation.consensus_level:.0%}",
            "",
            "Initial Positions:",
        ]

        for vote in votes:
            emoji = "+" if vote.score >= 6 else "-" if vote.score <= 4 else "~"
            lines.append(
                f"  [{emoji}] {vote.agent_name}: {vote.score}/10 "
                f"({vote.vote.value}) - {vote.reasoning[:80]}..."
            )

        return "\n".join(lines)


class StructuredDebatePhase(DebatePhase):
    """Phase 2: Orchestrator-moderated structured debate."""

    def __init__(
        self,
        time_manager: TimeManager,
        voting_system: VotingSystem,
        max_rounds: int = 3,
    ):
        super().__init__("structured_debate", time_manager, voting_system)
        self.max_rounds = max_rounds

    async def execute(
        self,
        idea: str,
        agents: dict[str, BaseAgent],
        context: dict[str, Any] | None = None,
        previous_results: list[PhaseResult] | None = None,
    ) -> PhaseResult:
        """Execute structured debate phase.

        Identifies key disagreements and facilitates focused discussion.
        """
        self.time_manager.start_phase(self.name)
        logger.info("Starting structured debate phase")

        # Get votes from Phase 1
        phase1_votes: list[AgentVote] = []
        phase1_responses: list[AgentResponse] = []

        if previous_results:
            for result in previous_results:
                if result.phase_name == "parallel_assessment":
                    phase1_votes = result.votes
                    phase1_responses = result.agent_responses
                    break

        # Identify key disagreements
        disagreements = self._identify_disagreements(phase1_votes)

        all_responses: list[AgentResponse] = []
        debate_rounds: list[dict[str, Any]] = []

        # Conduct debate rounds on each disagreement
        for round_num, topic in enumerate(disagreements[:self.max_rounds], 1):
            if self.time_manager.is_phase_expired:
                logger.warning("Phase time expired, ending debate early")
                break

            logger.info(
                "Debate round",
                round=round_num,
                topic=topic,
            )

            # Get relevant agents for this topic
            relevant_agents = self._get_relevant_agents(agents, topic)

            # Have agents debate this topic
            round_responses = await self._conduct_round(
                topic=topic,
                agents=relevant_agents,
                previous_responses=phase1_responses + all_responses,
                round_number=round_num,
            )

            all_responses.extend(round_responses)
            debate_rounds.append({
                "round": round_num,
                "topic": topic,
                "responses": len(round_responses),
            })

        # Devil's Advocate challenge
        devils_advocate = self._get_devils_advocate(agents)
        if devils_advocate:
            da_response = await devils_advocate.challenge_consensus(
                idea=idea,
                specialist_votes=phase1_votes,
                debate_history=all_responses,
            )
            all_responses.append(da_response)

        duration = self.time_manager.end_phase()

        summary = self._generate_summary(
            disagreements=disagreements,
            rounds=debate_rounds,
            da_participated=devils_advocate is not None,
        )

        logger.info(
            "Structured debate complete",
            rounds=len(debate_rounds),
            total_responses=len(all_responses),
            duration_seconds=duration,
        )

        return PhaseResult(
            phase_name=self.name,
            duration_seconds=duration,
            agent_responses=all_responses,
            votes=[],  # Updated votes come in Phase 3
            key_disagreements=disagreements,
            phase_summary=summary,
            metadata={"rounds": debate_rounds},
        )

    def _identify_disagreements(self, votes: list[AgentVote]) -> list[str]:
        """Identify key topics where agents disagree."""
        if len(votes) < 2:
            return ["general viability"]

        disagreements = []

        # Look for score disparities
        scores = [(v.agent_name, v.score) for v in votes]
        scores.sort(key=lambda x: x[1])

        if scores[-1][1] - scores[0][1] >= 3:
            disagreements.append(
                f"Overall viability (scores range {scores[0][1]} to {scores[-1][1]})"
            )

        # Look for conflicting insights
        all_red_flags = set()
        for vote in votes:
            all_red_flags.update(vote.red_flags)

        # Topics mentioned as red flags by some but not others
        common_topics = [
            "market timing",
            "unit economics",
            "technical feasibility",
            "competitive landscape",
            "team capability",
            "scalability",
        ]

        for topic in common_topics:
            mentions = sum(
                1 for flag in all_red_flags
                if topic.lower() in flag.lower()
            )
            if 0 < mentions < len(votes):
                disagreements.append(topic)

        # Always include at least one topic
        if not disagreements:
            disagreements.append("key success factors")

        return disagreements[:3]  # Top 3 disagreements

    def _get_relevant_agents(
        self,
        agents: dict[str, BaseAgent],
        topic: str,
    ) -> dict[str, BaseAgent]:
        """Get agents most relevant to a topic."""
        relevant = {}

        for agent_id, agent in agents.items():
            if isinstance(agent, DevilsAdvocateAgent):
                continue

            relevance = agent.get_domain_relevance(topic)
            if relevance >= 1.2:  # Above average relevance
                relevant[agent_id] = agent

        # Ensure at least 2 agents participate
        if len(relevant) < 2:
            for agent_id, agent in agents.items():
                if agent_id not in relevant and not isinstance(agent, DevilsAdvocateAgent):
                    relevant[agent_id] = agent
                if len(relevant) >= 2:
                    break

        return relevant

    async def _conduct_round(
        self,
        topic: str,
        agents: dict[str, BaseAgent],
        previous_responses: list[AgentResponse],
        round_number: int,
    ) -> list[AgentResponse]:
        """Conduct a single debate round."""
        # Sequential debate for this round
        round_responses = []

        for agent in agents.values():
            response = await agent.debate(
                topic=topic,
                other_positions=previous_responses + round_responses,
                round_number=round_number,
            )
            round_responses.append(response)

        return round_responses

    def _get_devils_advocate(
        self,
        agents: dict[str, BaseAgent],
    ) -> DevilsAdvocateAgent | None:
        """Get the Devil's Advocate agent if present."""
        for agent in agents.values():
            if isinstance(agent, DevilsAdvocateAgent):
                return agent
        return None

    def _generate_summary(
        self,
        disagreements: list[str],
        rounds: list[dict[str, Any]],
        da_participated: bool,
    ) -> str:
        """Generate debate phase summary."""
        lines = [
            f"Phase 2 Complete: {len(rounds)} debate rounds",
            "",
            "Topics Debated:",
        ]

        for topic in disagreements:
            lines.append(f"  - {topic}")

        if da_participated:
            lines.append("\nDevil's Advocate challenged the emerging consensus.")

        return "\n".join(lines)


class ConsensusPhase(DebatePhase):
    """Phase 3: Final voting and consensus building."""

    def __init__(
        self,
        time_manager: TimeManager,
        voting_system: VotingSystem,
    ):
        super().__init__("consensus_building", time_manager, voting_system)

    async def execute(
        self,
        idea: str,
        agents: dict[str, BaseAgent],
        context: dict[str, Any] | None = None,
        previous_results: list[PhaseResult] | None = None,
    ) -> PhaseResult:
        """Execute consensus building phase.

        All agents cast final votes based on the debate.
        """
        self.time_manager.start_phase(self.name)
        logger.info("Starting consensus building phase")

        # Build debate summary from previous phases
        debate_summary = self._build_debate_summary(previous_results or [])

        # Collect final votes from all specialists
        specialist_agents = {
            k: v for k, v in agents.items()
            if not isinstance(v, DevilsAdvocateAgent)
        }

        vote_tasks = [
            agent.final_vote(idea, debate_summary)
            for agent in specialist_agents.values()
        ]

        vote_results = await asyncio.gather(*vote_tasks, return_exceptions=True)

        # Process votes
        final_votes: list[AgentVote] = []
        for result, agent_id in zip(vote_results, specialist_agents.keys()):
            if isinstance(result, Exception):
                logger.error(
                    "Final vote failed",
                    agent=agent_id,
                    error=str(result),
                )
                continue
            final_votes.append(result)

        # Devil's Advocate final assessment
        devils_advocate = self._get_devils_advocate(agents)
        da_assessment = None
        da_response = None

        if devils_advocate and previous_results:
            da_challenges = [
                r for result in previous_results
                for r in result.agent_responses
                if r.agent_name == "Devil's Advocate"
            ]

            da_response = await devils_advocate.final_assessment(
                idea=idea,
                final_votes=final_votes,
                own_challenges=da_challenges,
            )
            da_assessment = da_response.content

        # Build consensus
        consensus = self.voting_system.build_consensus(
            final_votes,
            devils_advocate_assessment=da_assessment,
        )

        duration = self.time_manager.end_phase()

        # Generate summary
        summary = self._generate_summary(consensus, da_assessment)

        responses = []
        if da_response:
            responses.append(da_response)

        logger.info(
            "Consensus building complete",
            recommendation=consensus.recommendation.value,
            confidence=consensus.confidence,
            duration_seconds=duration,
        )

        return PhaseResult(
            phase_name=self.name,
            duration_seconds=duration,
            agent_responses=responses,
            votes=final_votes,
            phase_summary=summary,
            metadata={
                "consensus": consensus,
                "devils_advocate_assessment": da_assessment,
            },
        )

    def _build_debate_summary(self, previous_results: list[PhaseResult]) -> str:
        """Build a summary of the debate for final voting."""
        summaries = []

        for result in previous_results:
            summaries.append(f"## {result.phase_name.replace('_', ' ').title()}")
            summaries.append(result.phase_summary)
            summaries.append("")

            if result.key_disagreements:
                summaries.append("Key disagreements discussed:")
                for disagreement in result.key_disagreements:
                    summaries.append(f"  - {disagreement}")
                summaries.append("")

        return "\n".join(summaries)

    def _get_devils_advocate(
        self,
        agents: dict[str, BaseAgent],
    ) -> DevilsAdvocateAgent | None:
        """Get the Devil's Advocate agent if present."""
        for agent in agents.values():
            if isinstance(agent, DevilsAdvocateAgent):
                return agent
        return None

    def _generate_summary(
        self,
        consensus,  # ConsensusResult
        da_assessment: str | None,
    ) -> str:
        """Generate consensus phase summary."""
        rec_emoji = {
            "strong_go": "++",
            "go": "+",
            "conditional_go": "~",
            "no_go": "-",
            "strong_no_go": "--",
        }

        lines = [
            "Phase 3 Complete: Final Consensus",
            "",
            f"RECOMMENDATION: {consensus.recommendation.value.upper()} "
            f"{rec_emoji.get(consensus.recommendation.value, '')}",
            f"Confidence: {consensus.confidence:.0%}",
            f"Weighted Score: {consensus.weighted_score:.1f}/10",
            "",
            "Key Drivers:",
        ]

        for driver in consensus.key_drivers[:3]:
            lines.append(f"  + {driver}")

        lines.append("\nMajor Risks:")
        for risk in consensus.major_risks[:3]:
            lines.append(f"  - {risk}")

        if consensus.dissenting_opinions:
            lines.append(f"\nDissenting Opinions: {len(consensus.dissenting_opinions)} agent(s)")

        return "\n".join(lines)
