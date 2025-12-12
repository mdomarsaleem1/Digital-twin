"""FastAPI server for Agentic Council."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import structlog

from agentic_council import __version__
from agentic_council.orchestration.council import AgenticCouncil, CouncilConfig
from agentic_council.orchestration.voting import RiskAppetite
from agentic_council.evaluation.historical_tests import HistoricalTestRunner
from agentic_council.api.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    SessionResponse,
    TimeStatusResponse,
    AgentPositionsResponse,
    MetricsResponse,
    BacktestRequest,
    BacktestSummaryResponse,
    BacktestResultResponse,
    HealthResponse,
    ErrorResponse,
    ConsensusResponse,
    PhaseResultResponse,
    AgentVoteResponse,
    RecommendationEnum,
)

logger = structlog.get_logger()

# Global state
_council: AgenticCouncil | None = None
_test_runner: HistoricalTestRunner | None = None
_sessions: dict[str, Any] = {}
_active_evaluations: dict[str, asyncio.Task] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global _council, _test_runner

    logger.info("Starting Agentic Council API")

    # Initialize council
    try:
        _council = AgenticCouncil(
            config=CouncilConfig(
                total_time_seconds=900,
                risk_appetite=RiskAppetite.MODERATE,
            )
        )
        _test_runner = HistoricalTestRunner(_council)
        logger.info("Council initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize council", error=str(e))
        # Continue anyway for health check to work

    yield

    # Cleanup
    logger.info("Shutting down Agentic Council API")

    # Cancel any active evaluations
    for task in _active_evaluations.values():
        task.cancel()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Agentic Council API",
        description="Multi-agent council system for evaluating business ideas",
        version=__version__,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


# Health and Status Endpoints

@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Check API health status."""
    return HealthResponse(
        status="healthy" if _council else "degraded",
        version=__version__,
        models_configured=_council is not None,
        agents_count=len(_council.agents) if _council else 0,
    )


@app.get("/status/time", response_model=TimeStatusResponse, tags=["Status"])
async def get_time_status():
    """Get current debate time status."""
    if not _council:
        raise HTTPException(status_code=503, detail="Council not initialized")

    status = _council.get_time_status()
    return TimeStatusResponse(**status)


@app.get("/status/positions", response_model=AgentPositionsResponse, tags=["Status"])
async def get_agent_positions():
    """Get current agent positions."""
    if not _council:
        raise HTTPException(status_code=503, detail="Council not initialized")

    positions = _council.get_agent_positions()
    return AgentPositionsResponse(positions=positions)


# Evaluation Endpoints

@app.post("/evaluate", response_model=EvaluateResponse, tags=["Evaluation"])
async def evaluate_idea(request: EvaluateRequest, background_tasks: BackgroundTasks):
    """Evaluate a business idea through the council.

    This endpoint runs a full council evaluation including:
    - Phase 1: Parallel Assessment (all agents analyze independently)
    - Phase 2: Structured Debate (focused discussion on disagreements)
    - Phase 3: Consensus Building (final voting and recommendation)

    The evaluation typically takes 1-3 minutes depending on configuration.
    """
    if not _council:
        raise HTTPException(status_code=503, detail="Council not initialized")

    try:
        # Update risk appetite if specified
        if request.risk_appetite:
            _council.voting_system.risk_appetite = RiskAppetite(request.risk_appetite.value)

        # Run evaluation
        session = await _council.evaluate(
            idea=request.idea,
            context=request.context,
            session_id=request.session_id,
        )

        # Store session
        _sessions[session.session_id] = session

        # Build response
        consensus = session.final_consensus

        consensus_response = ConsensusResponse(
            recommendation=RecommendationEnum(consensus.recommendation.value),
            confidence=consensus.confidence,
            weighted_score=consensus.weighted_score,
            go_votes=consensus.aggregation.go_votes,
            no_go_votes=consensus.aggregation.no_go_votes,
            conditional_votes=consensus.aggregation.conditional_votes,
            consensus_level=consensus.aggregation.consensus_level,
            key_drivers=consensus.key_drivers,
            major_risks=consensus.major_risks,
            risk_assessment=consensus.risk_assessment,
        )

        phase_results = [
            PhaseResultResponse(
                phase_name=pr.phase_name,
                duration_seconds=pr.duration_seconds,
                agent_responses_count=len(pr.agent_responses),
                votes_count=len(pr.votes),
                summary=pr.phase_summary,
            )
            for pr in session.phase_results
        ]

        # Get final votes
        final_votes = []
        for pr in session.phase_results:
            if pr.phase_name == "consensus_building":
                for vote in pr.votes:
                    final_votes.append(AgentVoteResponse(
                        agent_name=vote.agent_name,
                        vote=vote.vote.value,
                        score=vote.score,
                        confidence=vote.confidence,
                        reasoning=vote.reasoning,
                        key_insights=vote.key_insights,
                        red_flags=vote.red_flags,
                    ))

        return EvaluateResponse(
            session_id=session.session_id,
            idea=session.idea,
            recommendation=RecommendationEnum(consensus.recommendation.value),
            confidence=consensus.confidence,
            weighted_score=consensus.weighted_score,
            consensus=consensus_response,
            phase_results=phase_results,
            agent_votes=final_votes,
            execution_time_seconds=session.duration_seconds,
            transcript=session.transcript,
        )

    except Exception as e:
        logger.error("Evaluation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}", response_model=SessionResponse, tags=["Evaluation"])
async def get_session(session_id: str):
    """Get details of a previous evaluation session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions[session_id]

    return SessionResponse(
        session_id=session.session_id,
        idea=session.idea,
        started_at=session.started_at,
        completed_at=session.completed_at,
        duration_seconds=session.duration_seconds,
        phase_count=len(session.phase_results),
        final_recommendation=RecommendationEnum(session.final_consensus.recommendation.value)
        if session.final_consensus else None,
        confidence=session.final_consensus.confidence if session.final_consensus else None,
    )


@app.get("/sessions", tags=["Evaluation"])
async def list_sessions(limit: int = 20, offset: int = 0):
    """List recent evaluation sessions."""
    sessions = list(_sessions.values())
    sessions.sort(key=lambda s: s.started_at, reverse=True)

    paginated = sessions[offset:offset + limit]

    return {
        "total": len(sessions),
        "limit": limit,
        "offset": offset,
        "sessions": [
            SessionResponse(
                session_id=s.session_id,
                idea=s.idea,
                started_at=s.started_at,
                completed_at=s.completed_at,
                duration_seconds=s.duration_seconds,
                phase_count=len(s.phase_results),
                final_recommendation=RecommendationEnum(s.final_consensus.recommendation.value)
                if s.final_consensus else None,
                confidence=s.final_consensus.confidence if s.final_consensus else None,
            )
            for s in paginated
        ],
    }


# Backtesting Endpoints

@app.post("/backtest", response_model=BacktestSummaryResponse, tags=["Backtesting"])
async def run_backtest(request: BacktestRequest):
    """Run historical backtests against the council.

    This evaluates the council's predictions against known outcomes
    from historical business cases (2008-2020).
    """
    if not _test_runner:
        raise HTTPException(status_code=503, detail="Test runner not initialized")

    try:
        if request.run_all:
            results = await _test_runner.run_all_tests(verbose=False)
        elif request.test_ids:
            results = []
            for test_id in request.test_ids:
                result = await _test_runner.run_test(test_id, verbose=False)
                results.append(result)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either run_all=true or test_ids must be provided"
            )

        stats = _test_runner.get_aggregate_stats()

        result_responses = [
            BacktestResultResponse(
                test_id=r.test_case.id,
                passed=r.passed,
                overall_accuracy=r.accuracy.overall_accuracy,
                direction_accuracy=r.accuracy.dimension_scores.direction,
                risk_precision=r.accuracy.dimension_scores.risk_precision,
                driver_accuracy=r.accuracy.dimension_scores.driver_accuracy,
                council_recommendation=r.session.final_consensus.recommendation.value
                if r.session.final_consensus else None,
                actual_success=r.test_case.actual_outcome.success,
                execution_time_seconds=r.execution_time_seconds,
            )
            for r in results
        ]

        return BacktestSummaryResponse(
            total_tests=stats["total_tests"],
            passed=stats["passed"],
            failed=stats["failed"],
            pass_rate=stats["pass_rate"],
            average_accuracy=stats["average_accuracy"],
            results=result_responses,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Backtest failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/backtest/cases", tags=["Backtesting"])
async def list_test_cases():
    """List available historical test cases."""
    if not _test_runner:
        raise HTTPException(status_code=503, detail="Test runner not initialized")

    cases = _test_runner.list_test_cases()
    return {"test_cases": cases}


# Metrics Endpoints

@app.get("/metrics", response_model=MetricsResponse, tags=["Metrics"])
async def get_metrics():
    """Get council performance metrics."""
    if not _test_runner:
        return MetricsResponse(
            total_sessions=len(_sessions),
            average_accuracy=None,
            average_execution_time=None,
            recommendation_distribution={},
        )

    stats = _test_runner.get_aggregate_stats()

    # Calculate recommendation distribution
    distribution: dict[str, int] = {}
    for session in _sessions.values():
        if session.final_consensus:
            rec = session.final_consensus.recommendation.value
            distribution[rec] = distribution.get(rec, 0) + 1

    # Calculate average execution time from sessions
    if _sessions:
        avg_time = sum(s.duration_seconds for s in _sessions.values()) / len(_sessions)
    else:
        avg_time = None

    return MetricsResponse(
        total_sessions=len(_sessions),
        average_accuracy=stats.get("average_accuracy"),
        average_execution_time=avg_time,
        recommendation_distribution=distribution,
    )


# Agent Info Endpoints

@app.get("/agents", tags=["Agents"])
async def list_agents():
    """List all council agents and their configurations."""
    if not _council:
        raise HTTPException(status_code=503, detail="Council not initialized")

    agents_info = []
    for agent_id, agent in _council.agents.items():
        agents_info.append({
            "id": agent_id,
            "name": agent.name,
            "role": agent.role,
            "focus_areas": agent.focus_areas,
            "domain_weights": agent.domain_weights,
        })

    return {"agents": agents_info}


# Error Handlers

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    logger.error("Unhandled exception", error=str(exc))
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc) if app.debug else None,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
