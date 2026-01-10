"""Output formatters for different formats (JSON, SARIF)."""

import json
from pathlib import Path
from typing import Any

from .models import Finding, GovernanceResult, Severity


class JSONFormatter:
    """Formats governance results as JSON."""

    def __init__(self, result: GovernanceResult):
        """Initialize formatter.

        Args:
            result: Governance result to format
        """
        self.result = result

    def format(self) -> str:
        """Format result as JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "version": "1.0",
            "spec_path": self.result.spec_path,
            "policy_name": self.result.policy_name,
            "status": self.result.status,
            "summary": {
                "total_findings": len(self.result.findings),
                "blockers": len(self.result.blockers),
                "majors": len(self.result.majors),
                "minors": len(self.result.minors),
                "infos": len(self.result.infos),
                "breaking_changes": len(self.result.breaking_changes),
            },
            "findings": [f.to_dict() for f in self.result.findings],
            "breaking_changes": [bc.to_dict() for bc in self.result.breaking_changes],
            "checklist": self.result.checklist,
        }

    def write(self, output_dir: Path) -> Path:
        """Write JSON to file.

        Args:
            output_dir: Output directory

        Returns:
            Path to generated file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "api-governor-report.json"
        path.write_text(self.format())
        return path


class SARIFFormatter:
    """Formats governance results as SARIF (Static Analysis Results Interchange Format)."""

    SARIF_VERSION = "2.1.0"
    SCHEMA_URI = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"

    def __init__(self, result: GovernanceResult):
        """Initialize formatter.

        Args:
            result: Governance result to format
        """
        self.result = result

    def format(self) -> str:
        """Format result as SARIF JSON string.

        Returns:
            SARIF JSON string
        """
        return json.dumps(self.to_sarif(), indent=2)

    def to_sarif(self) -> dict[str, Any]:
        """Convert result to SARIF format.

        Returns:
            SARIF document as dictionary
        """
        return {
            "$schema": self.SCHEMA_URI,
            "version": self.SARIF_VERSION,
            "runs": [self._create_run()],
        }

    def _create_run(self) -> dict[str, Any]:
        """Create a SARIF run object."""
        return {
            "tool": {
                "driver": {
                    "name": "API Governor",
                    "version": "1.0.0",
                    "informationUri": "https://github.com/akz4ol/api-governance-skill",
                    "rules": self._create_rules(),
                }
            },
            "results": self._create_results(),
            "invocations": [
                {
                    "executionSuccessful": self.result.status != "FAIL",
                    "toolExecutionNotifications": [],
                }
            ],
        }

    def _create_rules(self) -> list[dict[str, Any]]:
        """Create SARIF rule definitions from findings."""
        rules: dict[str, dict[str, Any]] = {}

        for finding in self.result.findings:
            if finding.rule_id not in rules:
                rules[finding.rule_id] = {
                    "id": finding.rule_id,
                    "name": finding.rule_id.replace("_", " ").title(),
                    "shortDescription": {"text": finding.message[:100]},
                    "defaultConfiguration": {
                        "level": self._severity_to_level(finding.severity)
                    },
                    "properties": {
                        "tags": ["api", "governance"],
                    },
                }

        return list(rules.values())

    def _create_results(self) -> list[dict[str, Any]]:
        """Create SARIF results from findings."""
        results = []

        for finding in self.result.findings:
            result: dict[str, Any] = {
                "ruleId": finding.rule_id,
                "level": self._severity_to_level(finding.severity),
                "message": {"text": finding.message},
            }

            # Add location if available
            if finding.path:
                location: dict[str, Any] = {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": self.result.spec_path,
                        },
                    },
                    "logicalLocations": [
                        {
                            "kind": "object",
                            "name": finding.path,
                        }
                    ],
                }

                if finding.line:
                    location["physicalLocation"]["region"] = {
                        "startLine": finding.line,
                    }

                result["locations"] = [location]

            # Add recommendation as fix suggestion
            if finding.recommendation:
                result["fixes"] = [
                    {
                        "description": {"text": finding.recommendation},
                    }
                ]

            results.append(result)

        # Add breaking changes as results
        for bc in self.result.breaking_changes:
            results.append(
                {
                    "ruleId": f"BREAK_{bc.change_type.upper()}",
                    "level": self._severity_to_level(bc.severity),
                    "message": {"text": f"Breaking change: {bc.description}"},
                    "locations": [
                        {
                            "logicalLocations": [
                                {
                                    "kind": "object",
                                    "name": bc.path,
                                }
                            ]
                        }
                    ],
                    "properties": {
                        "client_impact": bc.client_impact,
                    },
                }
            )

        return results

    def _severity_to_level(self, severity: Severity) -> str:
        """Convert severity to SARIF level.

        Args:
            severity: Finding severity

        Returns:
            SARIF level string
        """
        mapping = {
            Severity.BLOCKER: "error",
            Severity.MAJOR: "error",
            Severity.MINOR: "warning",
            Severity.INFO: "note",
        }
        return mapping.get(severity, "note")

    def write(self, output_dir: Path) -> Path:
        """Write SARIF to file.

        Args:
            output_dir: Output directory

        Returns:
            Path to generated file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "api-governor-report.sarif"
        path.write_text(self.format())
        return path


def format_result(
    result: GovernanceResult, output_format: str, output_dir: Path
) -> Path:
    """Format and write result in specified format.

    Args:
        result: Governance result
        output_format: Format (json, sarif, markdown)
        output_dir: Output directory

    Returns:
        Path to generated file
    """
    if output_format == "json":
        formatter = JSONFormatter(result)
        return formatter.write(output_dir)
    elif output_format == "sarif":
        formatter = SARIFFormatter(result)
        return formatter.write(output_dir)
    else:
        raise ValueError(f"Unknown format: {output_format}")
