"""Accuracy scoring for council predictions."""

from dataclasses import dataclass
from typing import Any


@dataclass
class DimensionScores:
    """Scores across different prediction dimensions."""
    direction: float  # Did council predict correct GO/NO-GO?
    risk_precision: float  # Did council identify actual risks?
    driver_accuracy: float  # Did council identify success factors?
    magnitude: float  # Market size estimation accuracy
    timing: float  # Did council identify timing importance?

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "direction": self.direction,
            "risk_precision": self.risk_precision,
            "driver_accuracy": self.driver_accuracy,
            "magnitude": self.magnitude,
            "timing": self.timing,
        }


@dataclass
class PredictionAccuracy:
    """Complete accuracy assessment."""
    overall_accuracy: float
    dimension_scores: DimensionScores
    correct_predictions: list[str]
    missed_predictions: list[str]
    false_positives: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_accuracy": self.overall_accuracy,
            "dimension_scores": self.dimension_scores.to_dict(),
            "correct_predictions": self.correct_predictions,
            "missed_predictions": self.missed_predictions,
            "false_positives": self.false_positives,
        }


class AccuracyScorer:
    """Scores prediction accuracy against actual outcomes."""

    def __init__(
        self,
        direction_weight: float = 0.3,
        risk_weight: float = 0.25,
        driver_weight: float = 0.2,
        magnitude_weight: float = 0.15,
        timing_weight: float = 0.1,
    ):
        """Initialize scorer with dimension weights.

        Args:
            direction_weight: Weight for direction accuracy
            risk_weight: Weight for risk identification
            driver_weight: Weight for success driver identification
            magnitude_weight: Weight for magnitude estimation
            timing_weight: Weight for timing assessment
        """
        self.weights = {
            "direction": direction_weight,
            "risk_precision": risk_weight,
            "driver_accuracy": driver_weight,
            "magnitude": magnitude_weight,
            "timing": timing_weight,
        }

    def score_prediction(
        self,
        council_output: dict[str, Any],
        actual_outcome: Any,  # ActualOutcome from historical_tests
    ) -> PredictionAccuracy:
        """Score a council prediction against actual outcome.

        Args:
            council_output: The council's prediction output
            actual_outcome: The known actual outcome

        Returns:
            PredictionAccuracy with detailed scores
        """
        scores = DimensionScores(
            direction=self._score_direction(council_output, actual_outcome),
            risk_precision=self._score_risk_precision(council_output, actual_outcome),
            driver_accuracy=self._score_driver_accuracy(council_output, actual_outcome),
            magnitude=self._score_magnitude(council_output, actual_outcome),
            timing=self._score_timing(council_output, actual_outcome),
        )

        # Calculate weighted overall score
        overall = (
            scores.direction * self.weights["direction"] +
            scores.risk_precision * self.weights["risk_precision"] +
            scores.driver_accuracy * self.weights["driver_accuracy"] +
            scores.magnitude * self.weights["magnitude"] +
            scores.timing * self.weights["timing"]
        )

        # Identify correct/missed predictions
        correct, missed, false_pos = self._analyze_predictions(
            council_output, actual_outcome
        )

        return PredictionAccuracy(
            overall_accuracy=overall,
            dimension_scores=scores,
            correct_predictions=correct,
            missed_predictions=missed,
            false_positives=false_pos,
        )

    def _score_direction(
        self,
        council_output: dict[str, Any],
        actual_outcome: Any,
    ) -> float:
        """Score direction accuracy (GO vs NO-GO).

        Returns 1.0 for correct, 0.0 for incorrect.
        """
        recommendation = council_output.get("recommendation", "").upper()
        is_go_prediction = recommendation == "GO"

        if is_go_prediction == actual_outcome.success:
            return 1.0
        return 0.0

    def _score_risk_precision(
        self,
        council_output: dict[str, Any],
        actual_outcome: Any,
    ) -> float:
        """Score risk identification accuracy.

        Measures overlap between predicted risks and actual failure reasons.
        """
        predicted_risks = set(
            self._normalize_text(r)
            for r in council_output.get("top_risks", [])
        )

        # For failures, check against failure reasons
        # For successes, check if risks were appropriately low
        if not actual_outcome.success:
            actual_issues = set(
                self._normalize_text(r)
                for r in actual_outcome.key_failure_reasons
            )

            if not actual_issues:
                return 0.5  # No actual issues to compare

            # Calculate Jaccard similarity
            intersection = len(self._fuzzy_match(predicted_risks, actual_issues))
            union = len(predicted_risks | actual_issues)

            if union == 0:
                return 0.5

            return intersection / union
        else:
            # For successes, fewer predicted risks is better
            if len(predicted_risks) == 0:
                return 1.0
            return max(0.0, 1.0 - len(predicted_risks) / 10)

    def _score_driver_accuracy(
        self,
        council_output: dict[str, Any],
        actual_outcome: Any,
    ) -> float:
        """Score success driver identification.

        Measures overlap between predicted drivers and actual success factors.
        """
        predicted_drivers = set(
            self._normalize_text(d)
            for d in council_output.get("success_drivers", [])
        )

        actual_drivers = set(
            self._normalize_text(d)
            for d in actual_outcome.key_success_factors
        )

        if not actual_drivers:
            # For failures, check if council correctly identified lack of drivers
            if not actual_outcome.success and len(predicted_drivers) <= 2:
                return 0.8
            return 0.5

        # Calculate overlap
        matches = len(self._fuzzy_match(predicted_drivers, actual_drivers))

        if len(actual_drivers) == 0:
            return 0.5

        return min(1.0, matches / len(actual_drivers))

    def _score_magnitude(
        self,
        council_output: dict[str, Any],
        actual_outcome: Any,
    ) -> float:
        """Score market size / magnitude estimation.

        Compares estimated TAM/valuation with actual market size achieved.
        """
        financial = council_output.get("financial_model", {})
        predicted_tam = financial.get("tam_estimate", 5.0)  # Default to middle

        actual_market = actual_outcome.market_size_achieved

        if actual_market == 0:
            # No market achieved - penalty for high predictions
            return max(0.0, 1.0 - predicted_tam / 10)

        # Score based on relative accuracy (log scale would be better)
        # Simple linear comparison for now
        ratio = predicted_tam / actual_market if actual_market > 0 else 1.0

        # Perfect score at ratio = 1, drops off either direction
        if ratio > 1:
            return max(0.0, 1.0 - (ratio - 1) / 2)
        else:
            return max(0.0, ratio)

    def _score_timing(
        self,
        council_output: dict[str, Any],
        actual_outcome: Any,
    ) -> float:
        """Score timing assessment accuracy.

        Checks if council identified timing as important when it was.
        """
        timing_critical = actual_outcome.timing_sensitivity

        # Check if council mentioned timing in key considerations
        considerations = " ".join(
            council_output.get("key_considerations", [])
        ).lower()

        top_risks = " ".join(
            council_output.get("top_risks", [])
        ).lower()

        timing_keywords = [
            "timing", "market timing", "too early", "too late",
            "window", "opportunity window", "trend", "tailwind",
            "headwind", "cycle", "momentum",
        ]

        timing_mentioned = any(
            kw in considerations or kw in top_risks
            for kw in timing_keywords
        )

        # Score based on alignment
        if timing_critical and timing_mentioned:
            return 1.0
        elif not timing_critical and not timing_mentioned:
            return 1.0
        elif timing_critical and not timing_mentioned:
            return 0.0  # Missed important timing factor
        else:
            return 0.5  # Over-emphasized timing

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        return text.lower().strip()

    def _fuzzy_match(
        self,
        set1: set[str],
        set2: set[str],
        threshold: float = 0.5,
    ) -> set[str]:
        """Find fuzzy matches between two sets of strings.

        Simple word overlap for now - could use more sophisticated
        similarity measures.
        """
        matches = set()

        for s1 in set1:
            words1 = set(s1.split())
            for s2 in set2:
                words2 = set(s2.split())
                if not words1 or not words2:
                    continue

                overlap = len(words1 & words2)
                total = len(words1 | words2)

                if total > 0 and overlap / total >= threshold:
                    matches.add(s1)
                    break

        return matches

    def _analyze_predictions(
        self,
        council_output: dict[str, Any],
        actual_outcome: Any,
    ) -> tuple[list[str], list[str], list[str]]:
        """Analyze which predictions were correct/missed.

        Returns:
            Tuple of (correct predictions, missed predictions, false positives)
        """
        predicted_risks = council_output.get("top_risks", [])
        predicted_drivers = council_output.get("success_drivers", [])

        actual_risks = actual_outcome.key_failure_reasons
        actual_drivers = actual_outcome.key_success_factors

        # Normalize for comparison
        predicted_all = set(self._normalize_text(p) for p in predicted_risks + predicted_drivers)
        actual_all = set(
            self._normalize_text(a)
            for a in actual_risks + actual_drivers
        )

        correct = []
        missed = []
        false_pos = []

        # Check predicted items
        for pred in predicted_all:
            if any(self._text_similarity(pred, actual) > 0.5 for actual in actual_all):
                correct.append(pred)
            else:
                false_pos.append(pred)

        # Check for missed actual items
        for actual in actual_all:
            if not any(self._text_similarity(actual, pred) > 0.5 for pred in predicted_all):
                missed.append(actual)

        return correct, missed, false_pos

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0
