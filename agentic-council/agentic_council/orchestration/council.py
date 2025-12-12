"""Main council orchestrator."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
import structlog

from agentic_council.models.base import BaseLLM
from agentic_council.models.model_factory import ModelFactory
from agentic_council.agents.base_agent import BaseAgent, AgentVote
from agentic_council.agents.specialists import create_specialist_agents
from agentic_council.agents.devils_advocate import DevilsAdvocateAgent
from agentic_council.orchestration.time_manager import TimeManager, PhaseTimeConfig, TimeoutAction
from agentic_council.orchestration.voting import VotingSystem, ConsensusResult, RiskAppetite
from agentic_council.orchestration.phases import (
    PhaseResult,
    ParallelAssessmentPhase,
    StructuredDebatePhase,
    ConsensusPhase,
)

logger = structlog.get_logger()


@dataclass
class CouncilConfig:
    """Configuration for the Agentic Council."""
    total_time_seconds: int = 900  # 15 minutes
    phase1_seconds: int = 300  # 5 minutes
    phase2_seconds: int = 420  # 7 minutes
    phase3_seconds: int = 180  # 3 minutes
    risk_appetite: RiskAppetite = RiskAppetite.MODERATE
    max_debate_rounds: int = 3
    enable_devils_advocate: bool = True

    @classmethod
    def from_yaml(cls, path: str | Path) -> "CouncilConfig":
        """Load config from YAML file."""
        with open(path) as f:
            config = yaml.safe_load(f)

        debate = config.get("debate", {})
        phases = debate.get("phases", {})

        return cls(
            total_time_seconds=debate.get("total_time_seconds", 900),
            phase1_seconds=phases.get("parallel_assessment", {}).get("duration_seconds", 300),
            phase2_seconds=phases.get("structured_debate", {}).get("duration_seconds", 420),
            phase3_seconds=phases.get("consensus_building", {}).get("duration_seconds", 180),
            risk_appetite=RiskAppetite(
                debate.get("consensus", {}).get("risk_appetite", "moderate").lower()
            ),
        )


@dataclass
class CouncilSession:
    """Represents a complete council session."""
    session_id: str
    idea: str
    context: dict[str, Any]
    started_at: datetime
    completed_at: datetime | None = None
    phase_results: list[PhaseResult] = field(default_factory=list)
    final_consensus: ConsensusResult | None = None
    transcript: list[dict[str, Any]] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        """Get session duration."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return (datetime.now() - self.started_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "idea": self.idea,
            "context": self.context,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "phase_count": len(self.phase_results),
            "final_recommendation": self.final_consensus.recommendation.value if self.final_consensus else None,
            "confidence": self.final_consensus.confidence if self.final_consensus else None,
        }


class AgenticCouncil:
    """Main orchestrator for the multi-agent council."""

    def __init__(
        self,
        config: CouncilConfig | None = None,
        orchestrator_llm: BaseLLM | None = None,
        specialist_llm: BaseLLM | None = None,
        devils_advocate_llm: BaseLLM | None = None,
    ):
        """Initialize the council.

        Args:
            config: Council configuration
            orchestrator_llm: LLM for the orchestrator (Claude)
            specialist_llm: LLM for specialist agents (Gemini)
            devils_advocate_llm: LLM for devil's advocate (Gemini Pro)
        """
        self.config = config or CouncilConfig()

        # Initialize LLMs
        self._init_llms(orchestrator_llm, specialist_llm, devils_advocate_llm)

        # Initialize agents
        self.agents: dict[str, BaseAgent] = {}
        self._init_agents()

        # Initialize time manager
        self.time_manager = TimeManager(
            total_time_seconds=self.config.total_time_seconds,
            phase_configs=[
                PhaseTimeConfig(
                    name="parallel_assessment",
                    duration_seconds=self.config.phase1_seconds,
                    timeout_action=TimeoutAction.SOFT_STOP,
                ),
                PhaseTimeConfig(
                    name="structured_debate",
                    duration_seconds=self.config.phase2_seconds,
                    timeout_action=TimeoutAction.SOFT_STOP,
                ),
                PhaseTimeConfig(
                    name="consensus_building",
                    duration_seconds=self.config.phase3_seconds,
                    timeout_action=TimeoutAction.HARD_STOP,
                ),
            ],
        )

        # Initialize voting system
        self.voting_system = VotingSystem(
            risk_appetite=self.config.risk_appetite,
        )

        # Initialize phases
        self.phases = {
            "parallel_assessment": ParallelAssessmentPhase(
                self.time_manager,
                self.voting_system,
            ),
            "structured_debate": StructuredDebatePhase(
                self.time_manager,
                self.voting_system,
                max_rounds=self.config.max_debate_rounds,
            ),
            "consensus_building": ConsensusPhase(
                self.time_manager,
                self.voting_system,
            ),
        }

        # Session tracking
        self._current_session: CouncilSession | None = None
        self._session_callbacks: list = []

    def _init_llms(
        self,
        orchestrator_llm: BaseLLM | None,
        specialist_llm: BaseLLM | None,
        devils_advocate_llm: BaseLLM | None,
    ) -> None:
        """Initialize LLM adapters."""
        # Default to creating adapters if not provided
        if orchestrator_llm:
            self.orchestrator_llm = orchestrator_llm
        else:
            self.orchestrator_llm = ModelFactory.create(
                provider="anthropic",
                model="claude-opus-4-5-20251101",
                max_tokens=4096,
                temperature=0.7,
            )

        if specialist_llm:
            self.specialist_llm = specialist_llm
        else:
            self.specialist_llm = ModelFactory.create(
                provider="google",
                model="gemini-2.0-flash-exp",
                max_tokens=2048,
                temperature=0.6,
            )

        if devils_advocate_llm:
            self.devils_advocate_llm = devils_advocate_llm
        else:
            self.devils_advocate_llm = ModelFactory.create(
                provider="google",
                model="gemini-1.5-pro",
                max_tokens=3072,
                temperature=0.8,
            )

    def _init_agents(self) -> None:
        """Initialize all council agents."""
        # Create specialist agents
        specialists = create_specialist_agents(self.specialist_llm)
        self.agents.update(specialists)

        # Create Devil's Advocate
        if self.config.enable_devils_advocate:
            self.agents["devils_advocate"] = DevilsAdvocateAgent(
                self.devils_advocate_llm
            )

        logger.info(
            "Council agents initialized",
            agent_count=len(self.agents),
            agents=list(self.agents.keys()),
        )

    async def evaluate(
        self,
        idea: str,
        context: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> CouncilSession:
        """Evaluate a business idea through the council.

        This is the main entry point for idea evaluation.

        Args:
            idea: The business idea to evaluate
            context: Additional context (market data, constraints, etc.)
            session_id: Optional session ID (auto-generated if not provided)

        Returns:
            CouncilSession with complete results
        """
        import uuid

        # Create session
        session_id = session_id or str(uuid.uuid4())[:8]
        self._current_session = CouncilSession(
            session_id=session_id,
            idea=idea,
            context=context or {},
            started_at=datetime.now(),
        )

        logger.info(
            "Council session started",
            session_id=session_id,
            idea_preview=idea[:100] + "..." if len(idea) > 100 else idea,
        )

        # Start overall timer
        self.time_manager.start()

        # Reset agent histories
        for agent in self.agents.values():
            agent.reset_history()

        try:
            # Phase 1: Parallel Assessment
            phase1_result = await self.phases["parallel_assessment"].execute(
                idea=idea,
                agents=self.agents,
                context=context,
            )
            self._current_session.phase_results.append(phase1_result)
            self._log_phase_complete(phase1_result)

            # Check if we should continue
            if self.time_manager.is_expired:
                logger.warning("Time expired after Phase 1, skipping remaining phases")
                return await self._finalize_session()

            # Phase 2: Structured Debate
            phase2_result = await self.phases["structured_debate"].execute(
                idea=idea,
                agents=self.agents,
                context=context,
                previous_results=self._current_session.phase_results,
            )
            self._current_session.phase_results.append(phase2_result)
            self._log_phase_complete(phase2_result)

            # Check if we should continue
            if self.time_manager.is_expired:
                logger.warning("Time expired after Phase 2, rushing to consensus")

            # Phase 3: Consensus Building
            phase3_result = await self.phases["consensus_building"].execute(
                idea=idea,
                agents=self.agents,
                context=context,
                previous_results=self._current_session.phase_results,
            )
            self._current_session.phase_results.append(phase3_result)
            self._log_phase_complete(phase3_result)

            # Extract final consensus
            self._current_session.final_consensus = phase3_result.metadata.get("consensus")

        except Exception as e:
            logger.error("Council evaluation failed", error=str(e))
            raise

        return await self._finalize_session()

    async def _finalize_session(self) -> CouncilSession:
        """Finalize the current session."""
        if not self._current_session:
            raise RuntimeError("No active session to finalize")

        self._current_session.completed_at = datetime.now()

        # Build transcript
        self._current_session.transcript = self._build_transcript()

        logger.info(
            "Council session completed",
            session_id=self._current_session.session_id,
            duration_seconds=self._current_session.duration_seconds,
            recommendation=self._current_session.final_consensus.recommendation.value
            if self._current_session.final_consensus else "incomplete",
        )

        return self._current_session

    def _log_phase_complete(self, result: PhaseResult) -> None:
        """Log phase completion."""
        logger.info(
            "Phase completed",
            phase=result.phase_name,
            duration_seconds=result.duration_seconds,
            responses=len(result.agent_responses),
            votes=len(result.votes),
        )

    def _build_transcript(self) -> list[dict[str, Any]]:
        """Build a transcript of the entire session."""
        transcript = []

        for phase_result in self._current_session.phase_results:
            # Phase header
            transcript.append({
                "type": "phase_start",
                "phase": phase_result.phase_name,
                "timestamp": None,  # Would need to track this
            })

            # Agent responses
            for response in phase_result.agent_responses:
                transcript.append({
                    "type": "agent_response",
                    "agent": response.agent_name,
                    "role": response.role,
                    "content": response.content,
                    "latency_ms": response.latency_ms,
                })

            # Votes
            for vote in phase_result.votes:
                transcript.append({
                    "type": "vote",
                    "agent": vote.agent_name,
                    "vote": vote.vote.value,
                    "score": vote.score,
                    "confidence": vote.confidence,
                    "reasoning": vote.reasoning,
                })

            # Phase summary
            transcript.append({
                "type": "phase_end",
                "phase": phase_result.phase_name,
                "summary": phase_result.phase_summary,
                "duration_seconds": phase_result.duration_seconds,
            })

        return transcript

    def get_time_status(self) -> dict[str, Any]:
        """Get current time status."""
        state = self.time_manager.get_state()
        return {
            "total_elapsed": state.total_elapsed,
            "total_remaining": state.remaining_total,
            "phase_elapsed": state.phase_elapsed,
            "phase_remaining": state.remaining_phase,
            "current_phase": state.current_phase,
            "progress_bar": self.time_manager.get_progress_bar(),
            "is_expired": state.is_expired,
        }

    def get_agent_positions(self) -> dict[str, dict[str, Any]]:
        """Get current positions of all agents."""
        if not self._current_session:
            return {}

        positions = {}

        # Get latest votes for each agent
        for phase_result in reversed(self._current_session.phase_results):
            for vote in phase_result.votes:
                if vote.agent_name not in positions:
                    positions[vote.agent_name] = {
                        "vote": vote.vote.value,
                        "score": vote.score,
                        "confidence": vote.confidence,
                        "reasoning": vote.reasoning[:200],
                    }

        return positions

    def register_callback(self, callback) -> None:
        """Register a callback for session updates."""
        self._session_callbacks.append(callback)

    @classmethod
    def from_config_files(
        cls,
        orchestration_path: str | Path,
        models_path: str | Path | None = None,
    ) -> "AgenticCouncil":
        """Create council from configuration files.

        Args:
            orchestration_path: Path to orchestration.yaml
            models_path: Path to models.yaml (optional)

        Returns:
            Configured AgenticCouncil instance
        """
        config = CouncilConfig.from_yaml(orchestration_path)

        llms = {}
        if models_path:
            llms = ModelFactory.from_config_file(models_path)

        return cls(
            config=config,
            orchestrator_llm=llms.get("orchestrator"),
            specialist_llm=llms.get("specialists"),
            devils_advocate_llm=llms.get("devils_advocate"),
        )
