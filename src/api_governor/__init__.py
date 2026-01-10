"""API Governor - OpenAPI governance and breaking change detection."""

__version__ = "1.0.0"

from .governor import APIGovernor
from .models import (
    Finding,
    Severity,
    GovernanceResult,
    BreakingChange,
    PolicyConfig,
)
from .parser import OpenAPIParser
from .rules import RuleEngine
from .diff import SpecDiffer

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
