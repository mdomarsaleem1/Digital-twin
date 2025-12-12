"""
Agentic Council System

A multi-agent council system for evaluating business ideas through
structured debate and consensus building.
"""

__version__ = "0.1.0"
__author__ = "Engineering Team"

from agentic_council.orchestration.council import AgenticCouncil
from agentic_council.models.base import LLMResponse

__all__ = ["AgenticCouncil", "LLMResponse"]
