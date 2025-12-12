"""Historical test cases for backtesting council predictions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json
from pathlib import Path

import structlog

from agentic_council.orchestration.council import AgenticCouncil, CouncilSession
from agentic_council.evaluation.accuracy_scorer import AccuracyScorer, PredictionAccuracy

logger = structlog.get_logger()


@dataclass
class ActualOutcome:
    """Known actual outcome of a business idea."""
    success: bool
    peak_valuation: str | None = None
    current_status: str = ""
    key_success_factors: list[str] = field(default_factory=list)
    key_failure_reasons: list[str] = field(default_factory=list)
    market_size_achieved: float = 0.0  # in billions
    timing_sensitivity: bool = False
    years_to_outcome: int = 0


@dataclass
class HistoricalTestCase:
    """A historical test case for backtesting."""
    id: str
    year: int
    idea: str
    context: str
    actual_outcome: ActualOutcome
    test_objective: str
    industry: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "year": self.year,
            "idea": self.idea,
            "context": self.context,
            "actual_outcome": {
                "success": self.actual_outcome.success,
                "peak_valuation": self.actual_outcome.peak_valuation,
                "current_status": self.actual_outcome.current_status,
                "key_success_factors": self.actual_outcome.key_success_factors,
                "key_failure_reasons": self.actual_outcome.key_failure_reasons,
            },
            "test_objective": self.test_objective,
            "industry": self.industry,
            "tags": self.tags,
        }


@dataclass
class TestResult:
    """Result of running a historical test."""
    test_case: HistoricalTestCase
    session: CouncilSession
    accuracy: PredictionAccuracy
    execution_time_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def passed(self) -> bool:
        """Check if direction prediction was correct."""
        return self.accuracy.dimension_scores.direction >= 0.5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_id": self.test_case.id,
            "passed": self.passed,
            "overall_accuracy": self.accuracy.overall_accuracy,
            "dimension_scores": {
                "direction": self.accuracy.dimension_scores.direction,
                "risk_precision": self.accuracy.dimension_scores.risk_precision,
                "driver_accuracy": self.accuracy.dimension_scores.driver_accuracy,
                "timing": self.accuracy.dimension_scores.timing,
            },
            "council_recommendation": self.session.final_consensus.recommendation.value
            if self.session.final_consensus else None,
            "actual_success": self.test_case.actual_outcome.success,
            "execution_time_seconds": self.execution_time_seconds,
            "timestamp": self.timestamp.isoformat(),
        }


class HistoricalTestRunner:
    """Runs historical backtests against the council."""

    def __init__(self, council: AgenticCouncil):
        """Initialize test runner.

        Args:
            council: The council to test
        """
        self.council = council
        self.scorer = AccuracyScorer()
        self._test_cases: dict[str, HistoricalTestCase] = {}
        self._results: list[TestResult] = []

        # Load default test cases
        self._load_default_cases()

    def _load_default_cases(self) -> None:
        """Load default historical test cases."""
        cases = [
            HistoricalTestCase(
                id="spotify_2008",
                year=2008,
                idea="Music streaming subscription service with a freemium model",
                context="""Post-Napster era, iTunes dominance with 70% market share,
                smartphone adoption at 30%, music piracy still prevalent,
                licensing costs unclear, broadband penetration growing.""",
                actual_outcome=ActualOutcome(
                    success=True,
                    peak_valuation="$70B",
                    current_status="Market leader in music streaming",
                    key_success_factors=[
                        "Freemium model drove viral adoption",
                        "Mobile-first approach aligned with smartphone growth",
                        "Playlist curation created discovery paradigm",
                        "Licensing deals with major labels",
                    ],
                    key_failure_reasons=[],
                    market_size_achieved=70.0,
                    timing_sensitivity=True,
                    years_to_outcome=15,
                ),
                test_objective="Would council predict success despite licensing concerns?",
                industry="music_streaming",
                tags=["streaming", "freemium", "mobile"],
            ),
            HistoricalTestCase(
                id="blue_apron_2012",
                year=2012,
                idea="Premium meal kit delivery service with subscription model",
                context="""E-commerce growing 15% YoY, logistics infrastructure improving,
                food culture shift toward home cooking, millennials seeking convenience,
                limited competition in meal kit space.""",
                actual_outcome=ActualOutcome(
                    success=False,
                    peak_valuation="$2B",
                    current_status="90% value destruction, near bankruptcy",
                    key_success_factors=[],
                    key_failure_reasons=[
                        "CAC too high ($94+)",
                        "Low retention (60% 6-month churn)",
                        "Operational complexity",
                        "Competition from Amazon, HelloFresh",
                    ],
                    market_size_achieved=0.3,
                    timing_sensitivity=False,
                    years_to_outcome=5,
                ),
                test_objective="Would council flag retention and unit economics risks?",
                industry="food_delivery",
                tags=["subscription", "logistics", "d2c"],
            ),
            HistoricalTestCase(
                id="bird_2017",
                year=2017,
                idea="On-demand electric scooter sharing in urban areas",
                context="""Uber/Lyft success proven, urbanization increasing,
                last-mile transportation problem unsolved, electric vehicle tech improving,
                sharing economy model validated.""",
                actual_outcome=ActualOutcome(
                    success=False,
                    peak_valuation="$2.5B",
                    current_status="Bankruptcy, acquired for ~$30M",
                    key_success_factors=[],
                    key_failure_reasons=[
                        "Vandalism and theft",
                        "Regulatory challenges",
                        "Unit economics never worked",
                        "Short scooter lifespan",
                    ],
                    market_size_achieved=0.5,
                    timing_sensitivity=False,
                    years_to_outcome=6,
                ),
                test_objective="Would council predict operational challenges?",
                industry="micromobility",
                tags=["mobility", "hardware", "sharing"],
            ),
            HistoricalTestCase(
                id="webflow_2017",
                year=2017,
                idea="No-code website builder targeting professional designers",
                context="""Developer shortage growing, democratization of tech trend,
                SaaS boom underway, Squarespace/Wix serving casual users,
                professional designers underserved.""",
                actual_outcome=ActualOutcome(
                    success=True,
                    peak_valuation="$4B+",
                    current_status="Strong growth, profitable",
                    key_success_factors=[
                        "Designer-focused positioning",
                        "CMS innovation",
                        "Education-led growth",
                        "Strong community",
                    ],
                    key_failure_reasons=[],
                    market_size_achieved=4.0,
                    timing_sensitivity=True,
                    years_to_outcome=7,
                ),
                test_objective="Would council identify niche positioning value?",
                industry="no_code",
                tags=["saas", "design", "no_code"],
            ),
            HistoricalTestCase(
                id="hopin_2020",
                year=2020,
                idea="Virtual events platform for conferences and meetings",
                context="""COVID-19 pandemic beginning, all events moving virtual,
                Zoom fatigue emerging, event industry in crisis,
                massive shift to remote work.""",
                actual_outcome=ActualOutcome(
                    success=False,
                    peak_valuation="$7.75B",
                    current_status="90% valuation drop, massive layoffs",
                    key_success_factors=[],
                    key_failure_reasons=[
                        "Pandemic tailwind was temporary",
                        "Weak retention post-pandemic",
                        "Over-raised at peak euphoria",
                        "Execution issues with M&A",
                    ],
                    market_size_achieved=0.8,
                    timing_sensitivity=True,
                    years_to_outcome=3,
                ),
                test_objective="Would council distinguish trend from sustainable demand?",
                industry="virtual_events",
                tags=["events", "remote", "covid"],
            ),
        ]

        for case in cases:
            self._test_cases[case.id] = case

        logger.info("Loaded historical test cases", count=len(cases))

    async def run_test(
        self,
        test_id: str,
        verbose: bool = False,
    ) -> TestResult:
        """Run a single historical test.

        Args:
            test_id: ID of the test case to run
            verbose: Print detailed output

        Returns:
            TestResult with accuracy scores
        """
        if test_id not in self._test_cases:
            raise ValueError(f"Unknown test case: {test_id}")

        test_case = self._test_cases[test_id]

        logger.info(
            "Running historical test",
            test_id=test_id,
            year=test_case.year,
            idea_preview=test_case.idea[:50],
        )

        # Build context for the council
        context = {
            "year": test_case.year,
            "market_context": test_case.context,
            "industry": test_case.industry,
            "backtest_mode": True,  # Signal to agents this is historical
        }

        # Run the council evaluation
        import time
        start_time = time.perf_counter()

        session = await self.council.evaluate(
            idea=test_case.idea,
            context=context,
        )

        execution_time = time.perf_counter() - start_time

        # Score the prediction
        accuracy = self.scorer.score_prediction(
            council_output=self._extract_council_output(session),
            actual_outcome=test_case.actual_outcome,
        )

        result = TestResult(
            test_case=test_case,
            session=session,
            accuracy=accuracy,
            execution_time_seconds=execution_time,
        )

        self._results.append(result)

        if verbose:
            self._print_result(result)

        logger.info(
            "Historical test completed",
            test_id=test_id,
            passed=result.passed,
            accuracy=accuracy.overall_accuracy,
        )

        return result

    async def run_all_tests(
        self,
        verbose: bool = False,
    ) -> list[TestResult]:
        """Run all historical tests.

        Args:
            verbose: Print detailed output

        Returns:
            List of all test results
        """
        results = []

        for test_id in self._test_cases:
            try:
                result = await self.run_test(test_id, verbose=verbose)
                results.append(result)
            except Exception as e:
                logger.error(
                    "Test failed",
                    test_id=test_id,
                    error=str(e),
                )

        # Summary
        passed = sum(1 for r in results if r.passed)
        avg_accuracy = (
            sum(r.accuracy.overall_accuracy for r in results) / len(results)
            if results else 0
        )

        logger.info(
            "All tests completed",
            total=len(results),
            passed=passed,
            failed=len(results) - passed,
            average_accuracy=avg_accuracy,
        )

        return results

    def _extract_council_output(self, session: CouncilSession) -> dict[str, Any]:
        """Extract council output for scoring.

        Args:
            session: The council session

        Returns:
            Structured output for scoring
        """
        consensus = session.final_consensus

        if not consensus:
            return {
                "recommendation": "unknown",
                "top_risks": [],
                "success_drivers": [],
                "financial_model": {"tam_estimate": 0},
                "key_considerations": [],
            }

        # Determine if recommendation is "GO" or "NO-GO"
        is_go = consensus.recommendation.value in [
            "strong_go", "go", "conditional_go"
        ]

        return {
            "recommendation": "GO" if is_go else "NO-GO",
            "confidence": consensus.confidence,
            "top_risks": consensus.major_risks,
            "success_drivers": consensus.key_drivers,
            "financial_model": {
                "tam_estimate": consensus.weighted_score,  # Proxy for market assessment
            },
            "key_considerations": [
                r.reasoning for r in consensus.dissenting_opinions
            ] if consensus.dissenting_opinions else [],
        }

    def _print_result(self, result: TestResult) -> None:
        """Print test result details."""
        tc = result.test_case
        acc = result.accuracy

        print(f"\n{'='*60}")
        print(f"TEST: {tc.id} ({tc.year})")
        print(f"IDEA: {tc.idea[:60]}...")
        print(f"{'='*60}")
        print(f"ACTUAL OUTCOME: {'SUCCESS' if tc.actual_outcome.success else 'FAILURE'}")
        print(f"COUNCIL PREDICTION: {result.session.final_consensus.recommendation.value.upper()}"
              if result.session.final_consensus else "INCOMPLETE")
        print(f"\nACCURACY SCORES:")
        print(f"  Direction:      {acc.dimension_scores.direction:.0%}")
        print(f"  Risk Precision: {acc.dimension_scores.risk_precision:.0%}")
        print(f"  Driver Accuracy:{acc.dimension_scores.driver_accuracy:.0%}")
        print(f"  Timing:         {acc.dimension_scores.timing:.0%}")
        print(f"\nOVERALL: {acc.overall_accuracy:.0%}")
        print(f"RESULT: {'PASSED' if result.passed else 'FAILED'}")
        print(f"{'='*60}\n")

    def get_aggregate_stats(self) -> dict[str, Any]:
        """Get aggregate statistics across all results.

        Returns:
            Dictionary of aggregate statistics
        """
        if not self._results:
            return {"total_tests": 0}

        results = self._results

        return {
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "pass_rate": sum(1 for r in results if r.passed) / len(results),
            "average_accuracy": sum(r.accuracy.overall_accuracy for r in results) / len(results),
            "average_direction_accuracy": sum(
                r.accuracy.dimension_scores.direction for r in results
            ) / len(results),
            "average_risk_precision": sum(
                r.accuracy.dimension_scores.risk_precision for r in results
            ) / len(results),
            "average_execution_time": sum(
                r.execution_time_seconds for r in results
            ) / len(results),
        }

    def add_test_case(self, case: HistoricalTestCase) -> None:
        """Add a new test case.

        Args:
            case: The test case to add
        """
        self._test_cases[case.id] = case
        logger.info("Test case added", test_id=case.id)

    def list_test_cases(self) -> list[str]:
        """List all available test case IDs."""
        return list(self._test_cases.keys())

    def save_results(self, path: str | Path) -> None:
        """Save test results to file.

        Args:
            path: Path to save results
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "aggregate_stats": self.get_aggregate_stats(),
            "results": [r.to_dict() for r in self._results],
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info("Results saved", path=str(path))
