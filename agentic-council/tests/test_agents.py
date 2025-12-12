"""Tests for agent implementations."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from agentic_council.agents.base_agent import BaseAgent, AgentVote, VoteType
from agentic_council.agents.specialists import (
    FinanceAgent,
    ProductAgent,
    EngineeringAgent,
    create_specialist_agents,
)
from agentic_council.agents.devils_advocate import DevilsAdvocateAgent
from agentic_council.models.base import BaseLLM, LLMResponse


@pytest.fixture
def mock_llm():
    """Create a mock LLM adapter."""
    llm = MagicMock(spec=BaseLLM)

    # Mock generate method
    async def mock_generate(*args, **kwargs):
        return LLMResponse(
            content="Test analysis content",
            model="test-model",
            provider="test",
            usage={"input_tokens": 100, "output_tokens": 200},
            latency_ms=500,
        )

    # Mock generate_structured method
    async def mock_generate_structured(*args, **kwargs):
        return {
            "vote": "go",
            "score": 7.0,
            "confidence": 0.8,
            "reasoning": "Test reasoning",
            "key_insights": ["Insight 1", "Insight 2"],
            "red_flags": ["Risk 1"],
            "domain_scores": {"market_size": 7.5},
        }

    llm.generate = AsyncMock(side_effect=mock_generate)
    llm.generate_structured = AsyncMock(side_effect=mock_generate_structured)

    return llm


class TestFinanceAgent:
    """Tests for Finance Agent."""

    def test_initialization(self, mock_llm):
        """Test agent initialization."""
        agent = FinanceAgent(mock_llm)

        assert agent.name == "CFO Agent"
        assert agent.role == "Chief Financial Officer"
        assert len(agent.focus_areas) > 0
        assert "financial_viability" in agent.domain_weights

    def test_domain_relevance_financial_topic(self, mock_llm):
        """Test domain relevance for financial topics."""
        agent = FinanceAgent(mock_llm)

        relevance = agent.get_domain_relevance("unit economics and revenue model")
        assert relevance >= 1.5

    def test_domain_relevance_unrelated_topic(self, mock_llm):
        """Test domain relevance for unrelated topics."""
        agent = FinanceAgent(mock_llm)

        relevance = agent.get_domain_relevance("user experience design")
        assert relevance == 1.0

    @pytest.mark.asyncio
    async def test_analyze(self, mock_llm):
        """Test idea analysis."""
        agent = FinanceAgent(mock_llm)

        response = await agent.analyze("A fintech app for budgeting")

        assert response.agent_name == "CFO Agent"
        assert response.phase == "parallel_assessment"
        assert response.vote is not None

    @pytest.mark.asyncio
    async def test_final_vote(self, mock_llm):
        """Test final voting."""
        agent = FinanceAgent(mock_llm)

        vote = await agent.final_vote(
            idea="A fintech app",
            debate_summary="Summary of debate"
        )

        assert isinstance(vote, AgentVote)
        assert vote.agent_name == "CFO Agent"
        assert 1 <= vote.score <= 10
        assert 0 <= vote.confidence <= 1


class TestProductAgent:
    """Tests for Product Agent."""

    def test_focus_areas(self, mock_llm):
        """Test product focus areas."""
        agent = ProductAgent(mock_llm)

        assert "Product-market fit signals" in agent.focus_areas
        assert "product_market_fit" in agent.domain_weights

    def test_domain_relevance(self, mock_llm):
        """Test product domain relevance."""
        agent = ProductAgent(mock_llm)

        assert agent.get_domain_relevance("product market fit") >= 2.0
        assert agent.get_domain_relevance("user experience") >= 2.0


class TestEngineeringAgent:
    """Tests for Engineering Agent."""

    def test_technical_domain(self, mock_llm):
        """Test technical domain weights."""
        agent = EngineeringAgent(mock_llm)

        assert agent.domain_weights["technical_feasibility"] == 2.0
        assert agent.domain_weights["scalability"] == 1.5

    def test_domain_relevance(self, mock_llm):
        """Test engineering domain relevance."""
        agent = EngineeringAgent(mock_llm)

        assert agent.get_domain_relevance("technical architecture") >= 2.0
        assert agent.get_domain_relevance("scalability concerns") >= 1.5


class TestDevilsAdvocate:
    """Tests for Devil's Advocate agent."""

    def test_initialization(self, mock_llm):
        """Test DA initialization."""
        agent = DevilsAdvocateAgent(mock_llm)

        assert agent.name == "Devil's Advocate"
        assert agent.always_oppose_majority is True
        assert agent.minimum_challenges >= 3

    def test_domain_relevance_all_topics(self, mock_llm):
        """Test DA has elevated relevance to all topics."""
        agent = DevilsAdvocateAgent(mock_llm)

        assert agent.get_domain_relevance("anything") == 1.5
        assert agent.get_domain_relevance("financial") == 1.5
        assert agent.get_domain_relevance("technical") == 1.5

    def test_determine_majority_go(self, mock_llm):
        """Test majority determination for GO votes."""
        agent = DevilsAdvocateAgent(mock_llm)

        votes = [
            AgentVote("A1", VoteType.GO, 7, 0.8, "", [], []),
            AgentVote("A2", VoteType.GO, 7, 0.8, "", [], []),
            AgentVote("A3", VoteType.NO_GO, 4, 0.7, "", [], []),
        ]

        majority = agent._determine_majority(votes)
        assert majority == "GO"

    def test_determine_majority_no_go(self, mock_llm):
        """Test majority determination for NO-GO votes."""
        agent = DevilsAdvocateAgent(mock_llm)

        votes = [
            AgentVote("A1", VoteType.NO_GO, 3, 0.8, "", [], []),
            AgentVote("A2", VoteType.NO_GO, 4, 0.8, "", [], []),
            AgentVote("A3", VoteType.GO, 7, 0.7, "", [], []),
        ]

        majority = agent._determine_majority(votes)
        assert majority == "NO_GO"


class TestSpecialistFactory:
    """Tests for specialist agent factory."""

    def test_create_all_specialists(self, mock_llm):
        """Test creating all specialist agents."""
        agents = create_specialist_agents(mock_llm)

        assert len(agents) == 6
        assert "finance" in agents
        assert "product" in agents
        assert "engineering" in agents
        assert "marketing" in agents
        assert "strategy" in agents
        assert "hr" in agents

    def test_specialists_share_llm(self, mock_llm):
        """Test all specialists share the same LLM."""
        agents = create_specialist_agents(mock_llm)

        for agent in agents.values():
            assert agent.llm is mock_llm
