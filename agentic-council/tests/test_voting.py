"""Tests for voting and consensus algorithms."""

import pytest
from agentic_council.agents.base_agent import AgentVote, VoteType
from agentic_council.orchestration.voting import (
    VotingSystem,
    RiskAppetite,
    Recommendation,
)


@pytest.fixture
def voting_system():
    """Create a voting system instance."""
    return VotingSystem(risk_appetite=RiskAppetite.MODERATE)


@pytest.fixture
def sample_votes():
    """Create sample votes for testing."""
    return [
        AgentVote(
            agent_name="CFO",
            vote=VoteType.GO,
            score=7.5,
            confidence=0.8,
            reasoning="Strong unit economics",
            key_insights=["Good margins", "Clear path to profitability"],
            red_flags=["High CAC"],
        ),
        AgentVote(
            agent_name="CPO",
            vote=VoteType.STRONG_GO,
            score=8.5,
            confidence=0.9,
            reasoning="Clear product-market fit",
            key_insights=["User demand validated", "MVP ready"],
            red_flags=[],
        ),
        AgentVote(
            agent_name="CTO",
            vote=VoteType.CONDITIONAL_GO,
            score=6.0,
            confidence=0.7,
            reasoning="Technically feasible with caveats",
            key_insights=["Standard tech stack"],
            red_flags=["Scalability concerns"],
        ),
        AgentVote(
            agent_name="CMO",
            vote=VoteType.GO,
            score=7.0,
            confidence=0.75,
            reasoning="Good market opportunity",
            key_insights=["Clear positioning"],
            red_flags=["Crowded market"],
        ),
        AgentVote(
            agent_name="CSO",
            vote=VoteType.GO,
            score=7.5,
            confidence=0.85,
            reasoning="Timing is right",
            key_insights=["Market trends favorable"],
            red_flags=[],
        ),
        AgentVote(
            agent_name="CHRO",
            vote=VoteType.NO_GO,
            score=4.0,
            confidence=0.6,
            reasoning="Team gaps",
            key_insights=[],
            red_flags=["Missing CTO", "Hiring challenges"],
        ),
    ]


class TestVoteAggregation:
    """Tests for vote aggregation."""

    def test_aggregate_empty_votes(self, voting_system):
        """Test aggregation with no votes."""
        aggregation = voting_system.aggregate_votes([])
        assert aggregation.total_votes == 0
        assert aggregation.weighted_score == 0.0

    def test_aggregate_votes_counts(self, voting_system, sample_votes):
        """Test vote count aggregation."""
        aggregation = voting_system.aggregate_votes(sample_votes)

        assert aggregation.total_votes == 6
        assert aggregation.go_votes == 4  # GO + STRONG_GO
        assert aggregation.no_go_votes == 1
        assert aggregation.conditional_votes == 1

    def test_aggregate_weighted_score(self, voting_system, sample_votes):
        """Test weighted score calculation."""
        aggregation = voting_system.aggregate_votes(sample_votes)

        # Weighted score should be between min and max scores
        assert aggregation.weighted_score >= 4.0
        assert aggregation.weighted_score <= 8.5

    def test_consensus_level(self, voting_system, sample_votes):
        """Test consensus level calculation."""
        aggregation = voting_system.aggregate_votes(sample_votes)

        # Consensus level should be between 0 and 1
        assert 0 <= aggregation.consensus_level <= 1

    def test_high_consensus(self, voting_system):
        """Test high consensus scenario."""
        unanimous_votes = [
            AgentVote(
                agent_name=f"Agent{i}",
                vote=VoteType.GO,
                score=7.5,
                confidence=0.9,
                reasoning="Agreement",
                key_insights=[],
                red_flags=[],
            )
            for i in range(5)
        ]

        aggregation = voting_system.aggregate_votes(unanimous_votes)
        assert aggregation.consensus_level > 0.9


class TestConsensusBuilding:
    """Tests for consensus building."""

    def test_build_consensus_go(self, voting_system, sample_votes):
        """Test consensus building with GO votes."""
        consensus = voting_system.build_consensus(sample_votes)

        # With majority GO votes, should recommend GO
        assert consensus.recommendation in [
            Recommendation.STRONG_GO,
            Recommendation.GO,
            Recommendation.CONDITIONAL_GO,
        ]

    def test_build_consensus_no_go(self, voting_system):
        """Test consensus building with NO-GO votes."""
        no_go_votes = [
            AgentVote(
                agent_name=f"Agent{i}",
                vote=VoteType.NO_GO,
                score=3.0,
                confidence=0.8,
                reasoning="Concerns",
                key_insights=[],
                red_flags=["Major risk"],
            )
            for i in range(5)
        ]

        consensus = voting_system.build_consensus(no_go_votes)
        assert consensus.recommendation in [
            Recommendation.NO_GO,
            Recommendation.STRONG_NO_GO,
        ]

    def test_dissenting_opinions(self, voting_system, sample_votes):
        """Test identification of dissenting opinions."""
        consensus = voting_system.build_consensus(sample_votes)

        # CHRO voted NO_GO, should be in dissenters
        dissenter_names = [d.agent_name for d in consensus.dissenting_opinions]
        assert "CHRO" in dissenter_names

    def test_key_drivers_extracted(self, voting_system, sample_votes):
        """Test extraction of key drivers."""
        consensus = voting_system.build_consensus(sample_votes)
        assert len(consensus.key_drivers) > 0

    def test_major_risks_extracted(self, voting_system, sample_votes):
        """Test extraction of major risks."""
        consensus = voting_system.build_consensus(sample_votes)
        assert len(consensus.major_risks) > 0


class TestRiskAppetite:
    """Tests for risk appetite effects."""

    def test_conservative_appetite(self, sample_votes):
        """Test conservative risk appetite."""
        system = VotingSystem(risk_appetite=RiskAppetite.CONSERVATIVE)
        consensus = system.build_consensus(sample_votes)

        # Conservative should weight risks more heavily
        assert consensus.confidence <= 0.9

    def test_aggressive_appetite(self, sample_votes):
        """Test aggressive risk appetite."""
        system = VotingSystem(risk_appetite=RiskAppetite.AGGRESSIVE)
        consensus = system.build_consensus(sample_votes)

        # Aggressive should be more willing to recommend GO
        assert consensus.recommendation in [
            Recommendation.STRONG_GO,
            Recommendation.GO,
            Recommendation.CONDITIONAL_GO,
        ]

    def test_risk_multiplier_values(self):
        """Test risk multiplier values are correct."""
        assert VotingSystem.RISK_APPETITE_WEIGHTS[RiskAppetite.CONSERVATIVE] < 1.0
        assert VotingSystem.RISK_APPETITE_WEIGHTS[RiskAppetite.MODERATE] == 1.0
        assert VotingSystem.RISK_APPETITE_WEIGHTS[RiskAppetite.AGGRESSIVE] > 1.0
