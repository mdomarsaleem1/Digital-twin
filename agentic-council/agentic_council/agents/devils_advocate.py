"""Devil's Advocate agent - challenges the emerging consensus."""

from typing import Any

from agentic_council.agents.base_agent import BaseAgent, AgentResponse, AgentVote, VoteType
from agentic_council.models.base import BaseLLM


class DevilsAdvocateAgent(BaseAgent):
    """Devil's Advocate Agent - Challenges the majority position."""

    PERSONA = """Your sole purpose is to challenge the emerging consensus. You look for blind spots,
hidden assumptions, and optimistic biases. You've studied hundreds of startup failures
and can pattern-match to warning signs. You are not negative by nature, but rigorously
skeptical.

CRITICAL RULE: When the majority says GO, you MUST present the strongest NO-GO case.
When the majority says NO-GO, you MUST present the strongest GO case.

You cite historical failures and successes to support your counterarguments.
You surface uncomfortable truths that others may be avoiding.
You are the last line of defense against groupthink."""

    FOCUS_AREAS = [
        "Challenge optimistic assumptions",
        "Identify hidden risks",
        "Reference historical failures",
        "Stress-test the consensus",
        "Surface uncomfortable truths",
    ]

    def __init__(self, llm: BaseLLM):
        super().__init__(
            name="Devil's Advocate",
            role="Critical Challenger",
            persona=self.PERSONA,
            llm=llm,
            domain_weights={},  # No domain-specific weights
            focus_areas=self.FOCUS_AREAS,
        )
        self.minimum_challenges = 3
        self.always_oppose_majority = True

    def get_domain_relevance(self, topic: str) -> float:
        """Devil's Advocate is equally relevant to all topics."""
        return 1.5  # Slightly elevated baseline

    async def challenge_consensus(
        self,
        idea: str,
        specialist_votes: list[AgentVote],
        debate_history: list[AgentResponse],
    ) -> AgentResponse:
        """Generate a challenge to the emerging consensus.

        This is the Devil's Advocate's primary function - to present
        the strongest possible case against the majority position.

        Args:
            idea: The business idea being evaluated
            specialist_votes: Votes from all specialist agents
            debate_history: Previous debate exchanges

        Returns:
            AgentResponse with the challenge
        """
        # Determine majority position
        majority_position = self._determine_majority(specialist_votes)

        # Build challenge prompt
        prompt = self._build_challenge_prompt(
            idea=idea,
            majority_position=majority_position,
            specialist_votes=specialist_votes,
            debate_history=debate_history,
        )

        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
        )

        return AgentResponse(
            agent_name=self.name,
            role=self.role,
            phase="devils_advocate_challenge",
            content=response.content,
            vote=None,
            llm_response=response,
            metadata={
                "majority_position": majority_position,
                "opposing_position": "NO_GO" if majority_position == "GO" else "GO",
            },
        )

    def _determine_majority(self, votes: list[AgentVote]) -> str:
        """Determine the majority position from votes.

        Returns:
            "GO" if majority favors proceeding, "NO_GO" otherwise
        """
        go_votes = sum(
            1 for v in votes
            if v.vote in [VoteType.STRONG_GO, VoteType.GO, VoteType.CONDITIONAL_GO]
        )
        no_go_votes = len(votes) - go_votes

        return "GO" if go_votes >= no_go_votes else "NO_GO"

    def _build_challenge_prompt(
        self,
        idea: str,
        majority_position: str,
        specialist_votes: list[AgentVote],
        debate_history: list[AgentResponse],
    ) -> str:
        """Build the challenge prompt."""
        # Format specialist votes
        votes_summary = self._format_votes_summary(specialist_votes)

        # Format debate highlights
        debate_highlights = self._format_debate_highlights(debate_history)

        # Determine opposing stance
        opposing_position = "NO_GO" if majority_position == "GO" else "GO"

        return f"""CHALLENGE THE CONSENSUS

BUSINESS IDEA:
{idea}

CURRENT MAJORITY POSITION: {majority_position}

SPECIALIST VOTES:
{votes_summary}

DEBATE HIGHLIGHTS:
{debate_highlights}

---

YOUR TASK: Present the strongest possible {opposing_position} case.

Since the majority favors {majority_position}, you MUST argue for {opposing_position}.

Your challenge should:
1. Identify at least {self.minimum_challenges} critical blind spots in the majority view
2. Reference specific historical examples of similar ideas that {"failed" if majority_position == "GO" else "succeeded despite skepticism"}
3. Challenge the key assumptions underlying the majority position
4. Present concrete risks or opportunities that have been underweighted
5. Offer a compelling narrative for why the consensus is wrong

Be rigorous and specific. This is not about being contrarian - it's about ensuring
the council has considered all perspectives before making a decision.

Remember: Great ideas have been killed by groupthink, and terrible ideas have been
pursued because no one dared to speak up. You are the guardian against both failures."""

    def _format_votes_summary(self, votes: list[AgentVote]) -> str:
        """Format votes into a readable summary."""
        lines = []
        for vote in votes:
            emoji = self._vote_emoji(vote.vote)
            lines.append(
                f"- {vote.agent_name}: {emoji} {vote.vote.value.upper()} "
                f"(Score: {vote.score}/10, Confidence: {vote.confidence:.0%})"
            )
            lines.append(f"  Reasoning: {vote.reasoning[:150]}...")
        return "\n".join(lines)

    def _format_debate_highlights(self, debate_history: list[AgentResponse]) -> str:
        """Extract key points from debate history."""
        if not debate_history:
            return "No debate history yet."

        highlights = []
        for response in debate_history[-6:]:  # Last 6 exchanges
            snippet = response.content[:200] + "..." if len(response.content) > 200 else response.content
            highlights.append(f"- {response.role}: {snippet}")

        return "\n".join(highlights)

    def _vote_emoji(self, vote: VoteType) -> str:
        """Get emoji for vote type."""
        return {
            VoteType.STRONG_GO: "++",
            VoteType.GO: "+",
            VoteType.CONDITIONAL_GO: "~",
            VoteType.NO_GO: "-",
            VoteType.STRONG_NO_GO: "--",
        }.get(vote, "?")

    async def final_assessment(
        self,
        idea: str,
        final_votes: list[AgentVote],
        own_challenges: list[AgentResponse],
    ) -> AgentResponse:
        """Provide final assessment after challenges.

        Unlike other agents, Devil's Advocate doesn't cast a binding vote
        but provides a final risk assessment.

        Args:
            idea: The business idea
            final_votes: Final votes from all specialists
            own_challenges: The challenges this agent raised

        Returns:
            Final assessment response
        """
        challenges_summary = "\n".join(
            f"- {c.content[:200]}..." for c in own_challenges
        )

        prompt = f"""FINAL RISK ASSESSMENT

BUSINESS IDEA:
{idea}

CHALLENGES I RAISED:
{challenges_summary}

FINAL SPECIALIST VOTES:
{self._format_votes_summary(final_votes)}

---

Provide your final assessment:

1. UNRESOLVED RISKS: Which of my challenges were NOT adequately addressed?

2. MITIGATED RISKS: Which challenges were successfully addressed by the council?

3. REMAINING BLIND SPOTS: Are there still perspectives the council hasn't considered?

4. CONFIDENCE IN OUTCOME: How confident are you that the council has made a well-informed decision?

5. KEY MONITORING POINTS: What should be closely watched if proceeding?

Note: You do NOT cast a binding vote. Your role is to ensure the decision is made with full awareness of risks."""

        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
        )

        return AgentResponse(
            agent_name=self.name,
            role=self.role,
            phase="final_assessment",
            content=response.content,
            vote=None,  # DA doesn't vote
            llm_response=response,
        )
