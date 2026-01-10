"""API Governor - OpenAPI governance and breaking change detection."""

__version__ = "1.0.0"

from .diff import SpecDiffer
from .governor import APIGovernor
from .models import (
    BreakingChange,
    Finding,
    GovernanceResult,
    PolicyConfig,
    Severity,
)
from .parser import OpenAPIParser
from .rules import RuleEngine

__all__ = [
    "APIGovernor",
    "Finding",
    "Severity",
    "GovernanceResult",
    "BreakingChange",
    "PolicyConfig",
    "OpenAPIParser",
    "RuleEngine",
    "SpecDiffer",
]
