"""Agent definitions for the council system."""

from agentic_council.agents.base_agent import BaseAgent, AgentResponse, AgentVote
from agentic_council.agents.specialists import (
    FinanceAgent,
    ProductAgent,
    EngineeringAgent,
    MarketingAgent,
    StrategyAgent,
    HRAgent,
)
from agentic_council.agents.devils_advocate import DevilsAdvocateAgent

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "AgentVote",
    "FinanceAgent",
    "ProductAgent",
    "EngineeringAgent",
    "MarketingAgent",
    "StrategyAgent",
    "HRAgent",
    "DevilsAdvocateAgent",
]
