"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskAppetiteEnum(str, Enum):
    """Risk appetite options."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class RecommendationEnum(str, Enum):
    """Recommendation types."""
    STRONG_GO = "strong_go"
    GO = "go"
    CONDITIONAL_GO = "conditional_go"
    NO_GO = "no_go"
    STRONG_NO_GO = "strong_no_go"


# Request Schemas

class EvaluateRequest(BaseModel):
    """Request to evaluate a business idea."""
    idea: str = Field(..., min_length=10, max_length=5000, description="The business idea to evaluate")
    context: dict[str, Any] | None = Field(default=None, description="Additional context")
    risk_appetite: RiskAppetiteEnum = Field(default=RiskAppetiteEnum.MODERATE, description="Risk tolerance")
    session_id: str | None = Field(default=None, description="Optional session ID")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "idea": "A mobile app that uses AI to recommend personalized workout routines based on user's fitness level and goals",
                    "context": {
                        "market": "fitness",
                        "target_users": "millennials and gen-z",
                        "budget": "$500K seed"
                    },
                    "risk_appetite": "moderate"
                }
            ]
        }
    }


class UserInterventionRequest(BaseModel):
    """Request for user intervention during debate."""
    session_id: str = Field(..., description="Session ID to intervene in")
    intervention_type: str = Field(..., description="Type of intervention")
    target_agent: str | None = Field(default=None, description="Target agent for question")
    content: str = Field(..., description="Intervention content")


class BacktestRequest(BaseModel):
    """Request to run a backtest."""
    test_ids: list[str] | None = Field(default=None, description="Specific test IDs to run")
    run_all: bool = Field(default=False, description="Run all available tests")


# Response Schemas

class AgentVoteResponse(BaseModel):
    """Agent vote response."""
    agent_name: str
    vote: str
    score: float
    confidence: float
    reasoning: str
    key_insights: list[str]
    red_flags: list[str]


class ConsensusResponse(BaseModel):
    """Consensus result response."""
    recommendation: RecommendationEnum
    confidence: float
    weighted_score: float
    go_votes: int
    no_go_votes: int
    conditional_votes: int
    consensus_level: float
    key_drivers: list[str]
    major_risks: list[str]
    risk_assessment: str


class PhaseResultResponse(BaseModel):
    """Phase result response."""
    phase_name: str
    duration_seconds: float
    agent_responses_count: int
    votes_count: int
    summary: str


class SessionResponse(BaseModel):
    """Session response."""
    session_id: str
    idea: str
    started_at: datetime
    completed_at: datetime | None
    duration_seconds: float
    phase_count: int
    final_recommendation: RecommendationEnum | None
    confidence: float | None


class EvaluateResponse(BaseModel):
    """Complete evaluation response."""
    session_id: str
    idea: str
    recommendation: RecommendationEnum
    confidence: float
    weighted_score: float
    consensus: ConsensusResponse
    phase_results: list[PhaseResultResponse]
    agent_votes: list[AgentVoteResponse]
    execution_time_seconds: float
    transcript: list[dict[str, Any]]


class TimeStatusResponse(BaseModel):
    """Current time status response."""
    total_elapsed: float
    total_remaining: float
    phase_elapsed: float
    phase_remaining: float
    current_phase: str
    progress_bar: str
    is_expired: bool


class AgentPositionsResponse(BaseModel):
    """Current agent positions response."""
    positions: dict[str, dict[str, Any]]


class MetricsResponse(BaseModel):
    """Council metrics response."""
    total_sessions: int
    average_accuracy: float | None
    average_execution_time: float | None
    recommendation_distribution: dict[str, int]


class BacktestResultResponse(BaseModel):
    """Single backtest result."""
    test_id: str
    passed: bool
    overall_accuracy: float
    direction_accuracy: float
    risk_precision: float
    driver_accuracy: float
    council_recommendation: str | None
    actual_success: bool
    execution_time_seconds: float


class BacktestSummaryResponse(BaseModel):
    """Backtest summary response."""
    total_tests: int
    passed: int
    failed: int
    pass_rate: float
    average_accuracy: float
    results: list[BacktestResultResponse]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    models_configured: bool
    agents_count: int


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: str | None = None
    code: str | None = None
