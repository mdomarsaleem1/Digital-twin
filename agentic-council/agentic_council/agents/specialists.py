"""Specialist agent implementations for the council."""

from agentic_council.agents.base_agent import BaseAgent
from agentic_council.models.base import BaseLLM


class FinanceAgent(BaseAgent):
    """CFO Agent - Expert in financial analysis and unit economics."""

    DOMAIN_WEIGHTS = {
        "financial_viability": 2.0,
        "market_size": 1.5,
        "capital_requirements": 2.0,
        "roi_potential": 1.8,
        "burn_rate": 2.0,
        "unit_economics": 2.0,
        "revenue_model": 1.8,
        "funding": 1.5,
    }

    FOCUS_AREAS = [
        "Unit economics (CAC, LTV, margins)",
        "Revenue model viability",
        "Funding requirements and runway",
        "Financial risk assessment",
        "Comparable company valuations",
    ]

    PERSONA = """You are a seasoned CFO with 20+ years of experience in venture capital,
corporate finance, and startup scaling. You think in terms of unit economics,
burn rates, runway, and capital efficiency. You've seen both successful exits
and spectacular failures, making you pragmatic about financial projections.

You always ask: "Does the math work?" You're skeptical of hockey-stick projections
and prefer to see realistic paths to profitability."""

    def __init__(self, llm: BaseLLM):
        super().__init__(
            name="CFO Agent",
            role="Chief Financial Officer",
            persona=self.PERSONA,
            llm=llm,
            domain_weights=self.DOMAIN_WEIGHTS,
            focus_areas=self.FOCUS_AREAS,
        )

    def get_domain_relevance(self, topic: str) -> float:
        """Get relevance score for a topic."""
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ["financial", "money", "revenue", "cost", "profit", "funding", "cac", "ltv", "burn", "unit economics"]):
            return 2.0
        if any(kw in topic_lower for kw in ["market size", "pricing", "monetization"]):
            return 1.5
        return 1.0


class ProductAgent(BaseAgent):
    """CPO Agent - Expert in product strategy and user experience."""

    DOMAIN_WEIGHTS = {
        "user_experience": 2.0,
        "product_market_fit": 2.0,
        "feature_scope": 1.5,
        "competitive_differentiation": 1.5,
        "user_research": 1.8,
        "mvp": 1.8,
        "iteration_strategy": 1.5,
    }

    FOCUS_AREAS = [
        "Product-market fit signals",
        "User experience and journey",
        "MVP scope and iteration strategy",
        "Competitive differentiation",
        "User research insights",
    ]

    PERSONA = """You are a product visionary who has built and scaled multiple successful products.
You obsess over user experience, product-market fit, and iterative development.
You've learned from failed products that ignored user feedback and succeeded
with those that nailed the core value proposition.

You always ask: "What problem does this solve and for whom?"
You're wary of feature bloat and emphasize the power of a focused MVP."""

    def __init__(self, llm: BaseLLM):
        super().__init__(
            name="CPO Agent",
            role="Chief Product Officer",
            persona=self.PERSONA,
            llm=llm,
            domain_weights=self.DOMAIN_WEIGHTS,
            focus_areas=self.FOCUS_AREAS,
        )

    def get_domain_relevance(self, topic: str) -> float:
        """Get relevance score for a topic."""
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ["product", "user", "feature", "ux", "experience", "mvp", "fit"]):
            return 2.0
        if any(kw in topic_lower for kw in ["customer", "market", "differentiation"]):
            return 1.5
        return 1.0


class EngineeringAgent(BaseAgent):
    """CTO Agent - Expert in technical architecture and feasibility."""

    DOMAIN_WEIGHTS = {
        "technical_feasibility": 2.0,
        "scalability": 1.5,
        "security": 1.5,
        "development_velocity": 1.5,
        "technical_debt": 1.8,
        "architecture": 2.0,
        "infrastructure": 1.5,
    }

    FOCUS_AREAS = [
        "Technical architecture and feasibility",
        "Scalability and performance",
        "Security and compliance",
        "Build vs buy decisions",
        "Development timeline realism",
    ]

    PERSONA = """You are a technical leader who has built systems from zero to millions of users.
You understand technical debt, scalability challenges, and the importance of
choosing the right architecture. You've seen projects fail due to over-engineering
and others succeed with pragmatic technical decisions.

You always ask: "Can we actually build this with available resources?"
You favor proven technologies and incremental complexity."""

    def __init__(self, llm: BaseLLM):
        super().__init__(
            name="CTO Agent",
            role="Chief Technology Officer",
            persona=self.PERSONA,
            llm=llm,
            domain_weights=self.DOMAIN_WEIGHTS,
            focus_areas=self.FOCUS_AREAS,
        )

    def get_domain_relevance(self, topic: str) -> float:
        """Get relevance score for a topic."""
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ["technical", "technology", "engineering", "architecture", "scalab", "security", "develop", "build"]):
            return 2.0
        if any(kw in topic_lower for kw in ["infrastructure", "api", "data", "system"]):
            return 1.5
        return 1.0


class MarketingAgent(BaseAgent):
    """CMO Agent - Expert in go-to-market and growth."""

    DOMAIN_WEIGHTS = {
        "go_to_market": 2.0,
        "competitive_positioning": 1.5,
        "viral_potential": 1.8,
        "brand_strategy": 1.5,
        "channel_strategy": 1.8,
        "customer_acquisition": 2.0,
        "retention": 1.5,
    }

    FOCUS_AREAS = [
        "Go-to-market strategy",
        "Customer acquisition channels",
        "Competitive positioning",
        "Brand and messaging",
        "Viral and growth loops",
    ]

    PERSONA = """You are a growth-focused marketing leader who understands both brand building
and performance marketing. You've launched products in crowded markets and
know what it takes to break through the noise. You think in terms of CAC,
viral coefficients, and market positioning.

You always ask: "How will customers discover this?"
You're skeptical of "build it and they will come" mentality."""

    def __init__(self, llm: BaseLLM):
        super().__init__(
            name="CMO Agent",
            role="Chief Marketing Officer",
            persona=self.PERSONA,
            llm=llm,
            domain_weights=self.DOMAIN_WEIGHTS,
            focus_areas=self.FOCUS_AREAS,
        )

    def get_domain_relevance(self, topic: str) -> float:
        """Get relevance score for a topic."""
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ["marketing", "growth", "acquisition", "brand", "viral", "channel", "position"]):
            return 2.0
        if any(kw in topic_lower for kw in ["customer", "market", "compet", "messaging"]):
            return 1.5
        return 1.0


class StrategyAgent(BaseAgent):
    """CSO Agent - Expert in strategic planning and market dynamics."""

    DOMAIN_WEIGHTS = {
        "strategic_alignment": 1.5,
        "market_timing": 2.0,
        "competitive_dynamics": 1.8,
        "partnership_potential": 1.5,
        "exit_potential": 1.5,
        "moat": 1.8,
        "market_trends": 1.8,
    }

    FOCUS_AREAS = [
        "Market timing and trends",
        "Competitive landscape analysis",
        "Strategic partnerships",
        "Long-term vision and moats",
        "Exit and scaling options",
    ]

    PERSONA = """You are a strategic thinker who sees the big picture. You understand market
dynamics, competitive landscapes, and timing. You've advised on M&A, pivots,
and market entries. You connect dots that others miss and think long-term.

You always ask: "Why now and why this team?"
You weigh in on most dimensions but specialize in seeing the forest for the trees."""

    # Strategy agent has a base weight on all dimensions
    ALL_DIMENSION_WEIGHT = 1.2

    def __init__(self, llm: BaseLLM):
        super().__init__(
            name="CSO Agent",
            role="Chief Strategy Officer",
            persona=self.PERSONA,
            llm=llm,
            domain_weights=self.DOMAIN_WEIGHTS,
            focus_areas=self.FOCUS_AREAS,
        )

    def get_domain_relevance(self, topic: str) -> float:
        """Get relevance score for a topic.

        Strategy agent has baseline relevance to all topics.
        """
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ["strategy", "timing", "competitive", "market", "moat", "exit", "partnership"]):
            return 2.0
        # Base relevance for all topics
        return self.ALL_DIMENSION_WEIGHT


class HRAgent(BaseAgent):
    """CHRO Agent - Expert in team and organizational dynamics."""

    DOMAIN_WEIGHTS = {
        "team_requirements": 2.0,
        "organizational_fit": 1.5,
        "talent_acquisition": 2.0,
        "culture_alignment": 1.5,
        "founder_team_assessment": 1.8,
        "hiring": 2.0,
        "organizational_scaling": 1.5,
    }

    FOCUS_AREAS = [
        "Team composition requirements",
        "Talent acquisition challenges",
        "Organizational culture",
        "Leadership assessment",
        "Scaling the team",
    ]

    PERSONA = """You are a people-focused leader who understands that great products are built
by great teams. You've seen startups fail due to culture issues, hiring mistakes,
and founder burnout. You think about talent acquisition, team dynamics, and
organizational scaling.

You always ask: "Does this team have what it takes?"
You're attuned to the human element that technical analysis often misses."""

    def __init__(self, llm: BaseLLM):
        super().__init__(
            name="CHRO Agent",
            role="Chief Human Resources Officer",
            persona=self.PERSONA,
            llm=llm,
            domain_weights=self.DOMAIN_WEIGHTS,
            focus_areas=self.FOCUS_AREAS,
        )

    def get_domain_relevance(self, topic: str) -> float:
        """Get relevance score for a topic."""
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ["team", "hiring", "talent", "culture", "people", "organization", "founder", "leadership"]):
            return 2.0
        if any(kw in topic_lower for kw in ["resource", "skill", "execution"]):
            return 1.5
        return 1.0


# Factory function for creating all specialists
def create_specialist_agents(llm: BaseLLM) -> dict[str, BaseAgent]:
    """Create all specialist agents with a shared LLM.

    Args:
        llm: The LLM adapter to use for all specialists

    Returns:
        Dictionary mapping agent IDs to agent instances
    """
    return {
        "finance": FinanceAgent(llm),
        "product": ProductAgent(llm),
        "engineering": EngineeringAgent(llm),
        "marketing": MarketingAgent(llm),
        "strategy": StrategyAgent(llm),
        "hr": HRAgent(llm),
    }
