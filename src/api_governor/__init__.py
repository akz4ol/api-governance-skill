"""API Governor - OpenAPI governance and breaking change detection."""

__version__ = "1.0.0"

from .diff import SpecDiffer
from .formatters import JSONFormatter, SARIFFormatter, format_result
from .governor import APIGovernor
from .models import (
    BreakingChange,
    Finding,
    GovernanceResult,
    PolicyConfig,
    Severity,
)
from .parser import OpenAPIParser
from .plugins import PluginManager, RulePlugin, default_manager
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
    "JSONFormatter",
    "SARIFFormatter",
    "format_result",
    "RulePlugin",
    "PluginManager",
    "default_manager",
]
