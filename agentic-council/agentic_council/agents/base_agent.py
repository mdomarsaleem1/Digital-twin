"""Base agent class for council members."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_council.models.base import BaseLLM, LLMResponse


class VoteType(str, Enum):
    """Vote options for agents."""
    STRONG_GO = "strong_go"
    GO = "go"
    CONDITIONAL_GO = "conditional_go"
    NO_GO = "no_go"
    STRONG_NO_GO = "strong_no_go"


@dataclass
class AgentVote:
    """An agent's vote on a business idea."""
    agent_name: str
    vote: VoteType
    score: float  # 1-10
    confidence: float  # 0-1
    reasoning: str
    key_insights: list[str]
    red_flags: list[str]
    domain_scores: dict[str, float] = field(default_factory=dict)

    @property
    def weighted_score(self) -> float:
        """Score weighted by confidence."""
        return self.score * self.confidence


@dataclass
class AgentResponse:
    """Full response from an agent."""
    agent_name: str
    role: str
    phase: str
    content: str
    vote: AgentVote | None = None
    llm_response: LLMResponse | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def latency_ms(self) -> float:
        """Get the LLM response latency."""
        if self.llm_response:
            return self.llm_response.latency_ms
        return 0.0


class BaseAgent(ABC):
    """Abstract base class for council agents."""

    def __init__(
        self,
        name: str,
        role: str,
        persona: str,
        llm: BaseLLM,
        domain_weights: dict[str, float] | None = None,
        focus_areas: list[str] | None = None,
    ):
        """Initialize an agent.

        Args:
            name: Agent's display name
            role: Agent's role (e.g., "CFO", "CTO")
            persona: Agent's persona description for the system prompt
            llm: The LLM adapter to use for generation
            domain_weights: Weights for different evaluation domains
            focus_areas: Areas this agent should focus on
        """
        self.name = name
        self.role = role
        self.persona = persona
        self.llm = llm
        self.domain_weights = domain_weights or {}
        self.focus_areas = focus_areas or []

        # Track conversation history for this agent
        self._history: list[dict[str, str]] = []

    @property
    def system_prompt(self) -> str:
        """Generate the system prompt for this agent."""
        focus_list = "\n".join(f"- {area}" for area in self.focus_areas)

        return f"""You are the {self.role} in a council evaluating business ideas.

{self.persona}

Your focus areas:
{focus_list}

When analyzing ideas:
1. Stay in your domain of expertise
2. Provide specific, actionable insights
3. Reference relevant examples or data when possible
4. Be direct and clear about risks and opportunities
5. Quantify your assessments when possible

Respond professionally and concisely."""

    async def analyze(
        self,
        idea: str,
        context: dict[str, Any] | None = None
    ) -> AgentResponse:
        """Perform initial analysis of a business idea.

        This is used in Phase 1 (Parallel Assessment).

        Args:
            idea: The business idea to evaluate
            context: Additional context (market data, constraints, etc.)

        Returns:
            AgentResponse with analysis and vote
        """
        prompt = self._build_analysis_prompt(idea, context)

        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
        )

        vote = await self._extract_vote(response.content, idea)

        return AgentResponse(
            agent_name=self.name,
            role=self.role,
            phase="parallel_assessment",
            content=response.content,
            vote=vote,
            llm_response=response,
        )

    async def debate(
        self,
        topic: str,
        other_positions: list[AgentResponse],
        round_number: int = 1
    ) -> AgentResponse:
        """Participate in structured debate.

        This is used in Phase 2 (Structured Debate).

        Args:
            topic: The specific topic being debated
            other_positions: Other agents' positions on this topic
            round_number: Which debate round this is

        Returns:
            AgentResponse with debate contribution
        """
        prompt = self._build_debate_prompt(topic, other_positions, round_number)

        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
        )

        # Store in history for context
        self._history.append({
            "role": "user",
            "content": prompt
        })
        self._history.append({
            "role": "assistant",
            "content": response.content
        })

        return AgentResponse(
            agent_name=self.name,
            role=self.role,
            phase="structured_debate",
            content=response.content,
            vote=None,  # Vote may be updated after debate
            llm_response=response,
            metadata={"round": round_number},
        )

    async def final_vote(
        self,
        idea: str,
        debate_summary: str
    ) -> AgentVote:
        """Cast final vote after debate.

        This is used in Phase 3 (Consensus Building).

        Args:
            idea: The original business idea
            debate_summary: Summary of the debate

        Returns:
            Final AgentVote
        """
        prompt = self._build_final_vote_prompt(idea, debate_summary)

        # Use structured output for final vote
        schema = {
            "type": "object",
            "properties": {
                "vote": {
                    "type": "string",
                    "enum": ["strong_go", "go", "conditional_go", "no_go", "strong_no_go"]
                },
                "score": {"type": "number", "minimum": 1, "maximum": 10},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "reasoning": {"type": "string"},
                "key_insights": {"type": "array", "items": {"type": "string"}},
                "red_flags": {"type": "array", "items": {"type": "string"}},
                "domain_scores": {
                    "type": "object",
                    "additionalProperties": {"type": "number"}
                }
            },
            "required": ["vote", "score", "confidence", "reasoning", "key_insights", "red_flags"]
        }

        result = await self.llm.generate_structured(
            prompt=prompt,
            schema=schema,
            system_prompt=self.system_prompt,
        )

        return AgentVote(
            agent_name=self.name,
            vote=VoteType(result["vote"]),
            score=result["score"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            key_insights=result["key_insights"],
            red_flags=result["red_flags"],
            domain_scores=result.get("domain_scores", {}),
        )

    def _build_analysis_prompt(
        self,
        idea: str,
        context: dict[str, Any] | None = None
    ) -> str:
        """Build the prompt for initial analysis."""
        context_str = ""
        if context:
            context_str = f"\n\nAdditional Context:\n{self._format_context(context)}"

        return f"""Analyze the following business idea from your perspective as {self.role}:

BUSINESS IDEA:
{idea}
{context_str}

Provide your analysis including:
1. Overall assessment (score 1-10 and confidence 0-1)
2. Key insights from your domain
3. Red flags or concerns
4. Specific recommendations

Be thorough but concise. Focus on your areas of expertise:
{', '.join(self.focus_areas)}"""

    def _build_debate_prompt(
        self,
        topic: str,
        other_positions: list[AgentResponse],
        round_number: int
    ) -> str:
        """Build the prompt for debate participation."""
        positions_str = "\n\n".join([
            f"**{pos.role}** ({pos.agent_name}):\n{pos.content}"
            for pos in other_positions
        ])

        return f"""DEBATE ROUND {round_number}

Topic under discussion:
{topic}

Other council members' positions:
{positions_str}

Based on your expertise as {self.role}, respond to these positions:
1. Do you agree or disagree with specific points?
2. What perspective are they missing from your domain?
3. What evidence or examples support your view?
4. Are there risks or opportunities others haven't considered?

Be direct and substantive. You may update your position based on compelling arguments."""

    def _build_final_vote_prompt(
        self,
        idea: str,
        debate_summary: str
    ) -> str:
        """Build the prompt for final voting."""
        return f"""Based on the complete council deliberation, cast your final vote.

ORIGINAL IDEA:
{idea}

DEBATE SUMMARY:
{debate_summary}

Cast your final vote considering:
1. Arguments from all council members
2. Your domain expertise and focus areas
3. The overall risk-reward profile

Provide your vote as JSON with:
- vote: one of [strong_go, go, conditional_go, no_go, strong_no_go]
- score: 1-10 rating
- confidence: 0-1 confidence in your assessment
- reasoning: brief explanation of your final position
- key_insights: top 3 insights from your analysis
- red_flags: any remaining concerns
- domain_scores: scores for your focus areas (e.g., {{"financial_viability": 7, "market_size": 8}})"""

    async def _extract_vote(self, content: str, idea: str) -> AgentVote:
        """Extract structured vote from free-form analysis.

        This converts the initial analysis into a structured vote.
        """
        schema = {
            "type": "object",
            "properties": {
                "vote": {
                    "type": "string",
                    "enum": ["strong_go", "go", "conditional_go", "no_go", "strong_no_go"]
                },
                "score": {"type": "number", "minimum": 1, "maximum": 10},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "reasoning": {"type": "string"},
                "key_insights": {"type": "array", "items": {"type": "string"}},
                "red_flags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["vote", "score", "confidence", "reasoning", "key_insights", "red_flags"]
        }

        prompt = f"""Based on the following analysis, extract the key information:

ANALYSIS:
{content}

Extract and structure the vote information as JSON."""

        result = await self.llm.generate_structured(
            prompt=prompt,
            schema=schema,
        )

        return AgentVote(
            agent_name=self.name,
            vote=VoteType(result["vote"]),
            score=result["score"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            key_insights=result["key_insights"],
            red_flags=result["red_flags"],
        )

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context dict into readable string."""
        lines = []
        for key, value in context.items():
            formatted_key = key.replace("_", " ").title()
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            elif isinstance(value, dict):
                value_str = ", ".join(f"{k}: {v}" for k, v in value.items())
            else:
                value_str = str(value)
            lines.append(f"- {formatted_key}: {value_str}")
        return "\n".join(lines)

    def reset_history(self) -> None:
        """Clear conversation history."""
        self._history.clear()

    @abstractmethod
    def get_domain_relevance(self, topic: str) -> float:
        """Calculate how relevant this agent is to a given topic.

        Args:
            topic: The topic or dimension being discussed

        Returns:
            Relevance score 0-2 (1 = neutral, >1 = highly relevant)
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, role={self.role})"
