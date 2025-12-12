"""Voting and consensus algorithms."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_council.agents.base_agent import AgentVote, VoteType


class Recommendation(str, Enum):
    """Final recommendation types."""
    STRONG_GO = "strong_go"
    GO = "go"
    CONDITIONAL_GO = "conditional_go"
    NO_GO = "no_go"
    STRONG_NO_GO = "strong_no_go"


class RiskAppetite(str, Enum):
    """Risk appetite levels for weighting."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class VoteAggregation:
    """Aggregated voting results."""
    total_votes: int
    weighted_score: float
    average_score: float
    average_confidence: float
    go_votes: int
    no_go_votes: int
    conditional_votes: int
    consensus_level: float  # 0-1, how aligned are the votes
    score_variance: float
    domain_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class ConsensusResult:
    """Final consensus result from voting."""
    recommendation: Recommendation
    confidence: float
    weighted_score: float
    aggregation: VoteAggregation
    risk_assessment: str
    dissenting_opinions: list[AgentVote]
    key_drivers: list[str]
    major_risks: list[str]


class VotingSystem:
    """Implements weighted voting and consensus algorithms."""

    # Score thresholds for recommendations
    RECOMMENDATION_THRESHOLDS = {
        Recommendation.STRONG_GO: 0.85,
        Recommendation.GO: 0.70,
        Recommendation.CONDITIONAL_GO: 0.55,
        Recommendation.NO_GO: 0.40,
        Recommendation.STRONG_NO_GO: 0.0,
    }

    # Risk appetite weight multipliers
    RISK_APPETITE_WEIGHTS = {
        RiskAppetite.CONSERVATIVE: 0.8,
        RiskAppetite.MODERATE: 1.0,
        RiskAppetite.AGGRESSIVE: 1.2,
    }

    def __init__(
        self,
        risk_appetite: RiskAppetite = RiskAppetite.MODERATE,
        domain_weights: dict[str, dict[str, float]] | None = None,
    ):
        """Initialize the voting system.

        Args:
            risk_appetite: The risk tolerance level
            domain_weights: Optional domain weights per agent
        """
        self.risk_appetite = risk_appetite
        self.domain_weights = domain_weights or {}
        self.risk_multiplier = self.RISK_APPETITE_WEIGHTS[risk_appetite]

    def aggregate_votes(
        self,
        votes: list[AgentVote],
        topic_relevance: dict[str, float] | None = None,
    ) -> VoteAggregation:
        """Aggregate votes from multiple agents.

        Args:
            votes: List of agent votes
            topic_relevance: Optional relevance scores per agent

        Returns:
            Aggregated voting statistics
        """
        if not votes:
            return VoteAggregation(
                total_votes=0,
                weighted_score=0.0,
                average_score=0.0,
                average_confidence=0.0,
                go_votes=0,
                no_go_votes=0,
                conditional_votes=0,
                consensus_level=0.0,
                score_variance=0.0,
            )

        # Calculate weights based on confidence and relevance
        weights = []
        for vote in votes:
            relevance = (topic_relevance or {}).get(vote.agent_name, 1.0)
            weight = vote.confidence * relevance
            weights.append(weight)

        total_weight = sum(weights)
        if total_weight == 0:
            total_weight = 1.0

        # Calculate weighted score
        weighted_score = sum(
            vote.score * weight for vote, weight in zip(votes, weights)
        ) / total_weight

        # Calculate average score and confidence
        average_score = sum(v.score for v in votes) / len(votes)
        average_confidence = sum(v.confidence for v in votes) / len(votes)

        # Count vote types
        go_votes = sum(
            1 for v in votes
            if v.vote in [VoteType.STRONG_GO, VoteType.GO]
        )
        no_go_votes = sum(
            1 for v in votes
            if v.vote in [VoteType.NO_GO, VoteType.STRONG_NO_GO]
        )
        conditional_votes = sum(
            1 for v in votes
            if v.vote == VoteType.CONDITIONAL_GO
        )

        # Calculate consensus level (inverse of variance)
        score_variance = self._calculate_variance([v.score for v in votes])
        # Max variance for 1-10 scale is ~20.25 (all 1s or all 10s)
        consensus_level = max(0.0, 1.0 - (score_variance / 20.0))

        # Aggregate domain scores
        domain_scores = self._aggregate_domain_scores(votes)

        return VoteAggregation(
            total_votes=len(votes),
            weighted_score=weighted_score,
            average_score=average_score,
            average_confidence=average_confidence,
            go_votes=go_votes,
            no_go_votes=no_go_votes,
            conditional_votes=conditional_votes,
            consensus_level=consensus_level,
            score_variance=score_variance,
            domain_scores=domain_scores,
        )

    def build_consensus(
        self,
        votes: list[AgentVote],
        devils_advocate_assessment: str | None = None,
    ) -> ConsensusResult:
        """Build final consensus from votes.

        Args:
            votes: List of final agent votes
            devils_advocate_assessment: Optional DA assessment

        Returns:
            ConsensusResult with recommendation
        """
        aggregation = self.aggregate_votes(votes)

        # Apply risk appetite adjustment
        adjusted_score = aggregation.weighted_score * self.risk_multiplier
        # Normalize to 0-1 scale (from 1-10)
        normalized_score = (adjusted_score - 1) / 9

        # Determine recommendation
        recommendation = self._score_to_recommendation(normalized_score)

        # Calculate confidence based on consensus level and average confidence
        confidence = (aggregation.consensus_level + aggregation.average_confidence) / 2

        # Find dissenting opinions
        dissenting = self._find_dissenters(votes, recommendation)

        # Extract key drivers and risks
        key_drivers = self._extract_key_drivers(votes)
        major_risks = self._extract_major_risks(votes)

        # Generate risk assessment text
        risk_assessment = self._generate_risk_assessment(
            aggregation, devils_advocate_assessment
        )

        return ConsensusResult(
            recommendation=recommendation,
            confidence=confidence,
            weighted_score=aggregation.weighted_score,
            aggregation=aggregation,
            risk_assessment=risk_assessment,
            dissenting_opinions=dissenting,
            key_drivers=key_drivers,
            major_risks=major_risks,
        )

    def _score_to_recommendation(self, normalized_score: float) -> Recommendation:
        """Convert normalized score to recommendation."""
        for rec, threshold in self.RECOMMENDATION_THRESHOLDS.items():
            if normalized_score >= threshold:
                return rec
        return Recommendation.STRONG_NO_GO

    def _find_dissenters(
        self,
        votes: list[AgentVote],
        recommendation: Recommendation,
    ) -> list[AgentVote]:
        """Find votes that disagree with the recommendation."""
        # Determine if recommendation is "go" or "no-go"
        is_go_recommendation = recommendation in [
            Recommendation.STRONG_GO,
            Recommendation.GO,
            Recommendation.CONDITIONAL_GO,
        ]

        dissenters = []
        for vote in votes:
            is_go_vote = vote.vote in [
                VoteType.STRONG_GO,
                VoteType.GO,
                VoteType.CONDITIONAL_GO,
            ]

            if is_go_vote != is_go_recommendation:
                dissenters.append(vote)

        return dissenters

    def _extract_key_drivers(self, votes: list[AgentVote]) -> list[str]:
        """Extract top key insights across all votes."""
        all_insights = []
        for vote in votes:
            all_insights.extend(vote.key_insights)

        # Return unique insights (deduplicated by similarity would be better)
        seen = set()
        unique = []
        for insight in all_insights:
            normalized = insight.lower().strip()[:50]
            if normalized not in seen:
                seen.add(normalized)
                unique.append(insight)

        return unique[:5]  # Top 5

    def _extract_major_risks(self, votes: list[AgentVote]) -> list[str]:
        """Extract top red flags across all votes."""
        all_flags = []
        for vote in votes:
            all_flags.extend(vote.red_flags)

        # Deduplicate
        seen = set()
        unique = []
        for flag in all_flags:
            normalized = flag.lower().strip()[:50]
            if normalized not in seen:
                seen.add(normalized)
                unique.append(flag)

        return unique[:5]  # Top 5

    def _aggregate_domain_scores(
        self,
        votes: list[AgentVote],
    ) -> dict[str, float]:
        """Aggregate domain scores across all agents."""
        domain_totals: dict[str, list[float]] = {}

        for vote in votes:
            for domain, score in vote.domain_scores.items():
                if domain not in domain_totals:
                    domain_totals[domain] = []
                domain_totals[domain].append(score)

        return {
            domain: sum(scores) / len(scores)
            for domain, scores in domain_totals.items()
        }

    def _calculate_variance(self, values: list[float]) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

    def _generate_risk_assessment(
        self,
        aggregation: VoteAggregation,
        devils_advocate_assessment: str | None,
    ) -> str:
        """Generate risk assessment text."""
        risk_level = "LOW" if aggregation.consensus_level > 0.8 else \
                     "MEDIUM" if aggregation.consensus_level > 0.5 else "HIGH"

        assessment = f"""Risk Level: {risk_level}

Consensus: {aggregation.consensus_level:.0%} agreement among council members
Vote Distribution: {aggregation.go_votes} GO, {aggregation.no_go_votes} NO-GO, {aggregation.conditional_votes} CONDITIONAL
Score Variance: {aggregation.score_variance:.2f} (lower is more aligned)
"""

        if devils_advocate_assessment:
            assessment += f"\nDevil's Advocate Notes:\n{devils_advocate_assessment[:500]}"

        return assessment

    def calculate_weighted_domain_score(
        self,
        vote: AgentVote,
        domain: str,
    ) -> float:
        """Calculate weighted score for a specific domain.

        Uses agent's domain weights to adjust scores.

        Args:
            vote: The agent's vote
            domain: The domain to score

        Returns:
            Weighted score for the domain
        """
        base_score = vote.domain_scores.get(domain, vote.score)

        # Get agent-specific weight for this domain
        agent_weights = self.domain_weights.get(vote.agent_name, {})
        weight = agent_weights.get(domain, 1.0)

        return base_score * weight * vote.confidence
