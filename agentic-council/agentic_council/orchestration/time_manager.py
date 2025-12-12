"""Time management for debate phases."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Callable, Any
from enum import Enum

import structlog

logger = structlog.get_logger()


class TimeoutAction(str, Enum):
    """What to do when time runs out."""
    HARD_STOP = "hard_stop"  # Immediately end
    WARN_CONTINUE = "warn_continue"  # Warn but allow completion
    SOFT_STOP = "soft_stop"  # Allow current operation to finish


@dataclass
class PhaseTimeConfig:
    """Configuration for a phase's time constraints."""
    name: str
    duration_seconds: int
    timeout_action: TimeoutAction = TimeoutAction.SOFT_STOP
    warning_threshold: float = 0.8  # Warn at 80% of time


@dataclass
class TimeState:
    """Current state of time tracking."""
    total_elapsed: float = 0.0
    phase_elapsed: float = 0.0
    remaining_total: float = 0.0
    remaining_phase: float = 0.0
    current_phase: str = ""
    is_expired: bool = False
    warning_issued: bool = False


class TimeManager:
    """Manages time constraints for council debates."""

    def __init__(
        self,
        total_time_seconds: int = 900,  # 15 minutes default
        phase_configs: list[PhaseTimeConfig] | None = None,
    ):
        """Initialize the time manager.

        Args:
            total_time_seconds: Total time allowed for the entire debate
            phase_configs: Optional time configs for each phase
        """
        self.total_time_seconds = total_time_seconds
        self.phase_configs = {
            config.name: config for config in (phase_configs or [])
        }

        self._start_time: float | None = None
        self._phase_start_time: float | None = None
        self._current_phase: str = ""
        self._callbacks: list[Callable[[TimeState], None]] = []

    def start(self) -> None:
        """Start the overall timer."""
        self._start_time = time.perf_counter()
        logger.info("Debate timer started", total_seconds=self.total_time_seconds)

    def start_phase(self, phase_name: str) -> None:
        """Start timing a specific phase.

        Args:
            phase_name: Name of the phase starting
        """
        self._phase_start_time = time.perf_counter()
        self._current_phase = phase_name

        config = self.phase_configs.get(phase_name)
        duration = config.duration_seconds if config else "unlimited"

        logger.info(
            "Phase started",
            phase=phase_name,
            duration_seconds=duration,
            total_elapsed=self.total_elapsed,
        )

    def end_phase(self) -> float:
        """End the current phase.

        Returns:
            Duration of the completed phase in seconds
        """
        duration = self.phase_elapsed
        logger.info(
            "Phase completed",
            phase=self._current_phase,
            duration_seconds=duration,
        )
        self._current_phase = ""
        self._phase_start_time = None
        return duration

    @property
    def total_elapsed(self) -> float:
        """Get total elapsed time in seconds."""
        if self._start_time is None:
            return 0.0
        return time.perf_counter() - self._start_time

    @property
    def phase_elapsed(self) -> float:
        """Get elapsed time in current phase."""
        if self._phase_start_time is None:
            return 0.0
        return time.perf_counter() - self._phase_start_time

    @property
    def total_remaining(self) -> float:
        """Get remaining total time."""
        return max(0.0, self.total_time_seconds - self.total_elapsed)

    @property
    def phase_remaining(self) -> float:
        """Get remaining time in current phase."""
        config = self.phase_configs.get(self._current_phase)
        if config is None:
            return float("inf")
        return max(0.0, config.duration_seconds - self.phase_elapsed)

    @property
    def is_expired(self) -> bool:
        """Check if total time has expired."""
        return self.total_remaining <= 0

    @property
    def is_phase_expired(self) -> bool:
        """Check if current phase time has expired."""
        return self.phase_remaining <= 0

    def get_state(self) -> TimeState:
        """Get current time state."""
        return TimeState(
            total_elapsed=self.total_elapsed,
            phase_elapsed=self.phase_elapsed,
            remaining_total=self.total_remaining,
            remaining_phase=self.phase_remaining,
            current_phase=self._current_phase,
            is_expired=self.is_expired,
        )

    def should_warn(self) -> bool:
        """Check if we should issue a time warning."""
        config = self.phase_configs.get(self._current_phase)
        if config is None:
            return False

        elapsed_ratio = self.phase_elapsed / config.duration_seconds
        return elapsed_ratio >= config.warning_threshold

    async def with_timeout(
        self,
        coro,
        phase_name: str | None = None,
        fallback: Any = None,
    ):
        """Run a coroutine with timeout.

        Args:
            coro: The coroutine to run
            phase_name: Optional phase name for phase-specific timeout
            fallback: Value to return on timeout

        Returns:
            Result of the coroutine or fallback on timeout
        """
        # Determine timeout
        if phase_name and phase_name in self.phase_configs:
            timeout = self.phase_configs[phase_name].duration_seconds
        else:
            timeout = self.total_remaining

        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(
                "Operation timed out",
                phase=phase_name or "overall",
                timeout_seconds=timeout,
            )
            return fallback

    def register_callback(self, callback: Callable[[TimeState], None]) -> None:
        """Register a callback for time updates.

        Args:
            callback: Function to call with TimeState updates
        """
        self._callbacks.append(callback)

    def notify_callbacks(self) -> None:
        """Notify all registered callbacks of current state."""
        state = self.get_state()
        for callback in self._callbacks:
            try:
                callback(state)
            except Exception as e:
                logger.error("Callback error", error=str(e))

    def format_remaining(self) -> str:
        """Format remaining time as MM:SS string."""
        total_seconds = int(self.total_remaining)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_progress_bar(self, width: int = 20) -> str:
        """Get a text progress bar for time.

        Args:
            width: Width of the progress bar

        Returns:
            String representation of progress
        """
        elapsed_ratio = min(1.0, self.total_elapsed / self.total_time_seconds)
        filled = int(width * elapsed_ratio)
        empty = width - filled

        bar = "=" * filled + "-" * empty
        return f"[{bar}] {self.format_remaining()}"
