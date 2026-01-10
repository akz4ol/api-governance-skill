"""Data models for API Governor."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(Enum):
    """Finding severity levels."""

    BLOCKER = "BLOCKER"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"


@dataclass
class Finding:
    """A governance finding."""

    rule_id: str
    severity: Severity
    message: str
    path: str | None = None
    line: int | None = None
    recommendation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message,
            "path": self.path,
            "line": self.line,
            "recommendation": self.recommendation,
        }


@dataclass
class BreakingChange:
    """A breaking change between spec versions."""

    change_type: str
    path: str
    description: str
    client_impact: str
    severity: Severity = Severity.MAJOR

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "change_type": self.change_type,
            "path": self.path,
            "description": self.description,
            "client_impact": self.client_impact,
            "severity": self.severity.value,
        }


@dataclass
class GovernanceResult:
    """Result of governance analysis."""

    spec_path: str
    policy_name: str
    status: str  # PASS, WARN, FAIL
    findings: list[Finding] = field(default_factory=list)
    breaking_changes: list[BreakingChange] = field(default_factory=list)
    checklist: dict[str, bool] = field(default_factory=dict)

    @property
    def blockers(self) -> list[Finding]:
        """Get all BLOCKER findings."""
        return [f for f in self.findings if f.severity == Severity.BLOCKER]

    @property
    def majors(self) -> list[Finding]:
        """Get all MAJOR findings."""
        return [f for f in self.findings if f.severity == Severity.MAJOR]

    @property
    def minors(self) -> list[Finding]:
        """Get all MINOR findings."""
        return [f for f in self.findings if f.severity == Severity.MINOR]

    @property
    def infos(self) -> list[Finding]:
        """Get all INFO findings."""
        return [f for f in self.findings if f.severity == Severity.INFO]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "spec_path": self.spec_path,
            "policy_name": self.policy_name,
            "status": self.status,
            "findings": [f.to_dict() for f in self.findings],
            "breaking_changes": [bc.to_dict() for bc in self.breaking_changes],
            "checklist": self.checklist,
        }


@dataclass
class PolicyConfig:
    """Policy configuration."""

    name: str
    version: str
    config: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PolicyConfig":
        """Create from dictionary."""
        return cls(
            name=data.get("policy_name", "Unknown"),
            version=data.get("policy_version", "0.0"),
            config=data,
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
