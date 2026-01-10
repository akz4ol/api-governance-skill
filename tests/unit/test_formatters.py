"""Tests for output formatters."""

import json
from pathlib import Path

from api_governor.formatters import JSONFormatter, SARIFFormatter
from api_governor.models import Finding, GovernanceResult, Severity


class TestJSONFormatter:
    """Tests for JSONFormatter class."""

    def test_format_empty_result(self) -> None:
        """Test formatting empty result."""
        result = GovernanceResult(
            spec_path="openapi.yaml",
            policy_name="test",
            status="PASS",
        )

        formatter = JSONFormatter(result)
        output = formatter.format()

        parsed = json.loads(output)
        assert parsed["status"] == "PASS"
        assert parsed["summary"]["total_findings"] == 0

    def test_format_with_findings(self) -> None:
        """Test formatting result with findings."""
        result = GovernanceResult(
            spec_path="openapi.yaml",
            policy_name="test",
            status="FAIL",
            findings=[
                Finding(
                    rule_id="SEC001",
                    severity=Severity.BLOCKER,
                    message="Missing authentication",
                    path="/users",
                )
            ],
        )

        formatter = JSONFormatter(result)
        output = formatter.format()

        parsed = json.loads(output)
        assert parsed["status"] == "FAIL"
        assert parsed["summary"]["blockers"] == 1
        assert len(parsed["findings"]) == 1
        assert parsed["findings"][0]["rule_id"] == "SEC001"

    def test_write_to_file(self, tmp_path: Path) -> None:
        """Test writing JSON to file."""
        result = GovernanceResult(
            spec_path="openapi.yaml",
            policy_name="test",
            status="PASS",
        )

        formatter = JSONFormatter(result)
        path = formatter.write(tmp_path)

        assert path.exists()
        assert path.name == "api-governor-report.json"


class TestSARIFFormatter:
    """Tests for SARIFFormatter class."""

    def test_sarif_structure(self) -> None:
        """Test SARIF output has correct structure."""
        result = GovernanceResult(
            spec_path="openapi.yaml",
            policy_name="test",
            status="PASS",
        )

        formatter = SARIFFormatter(result)
        output = formatter.format()

        parsed = json.loads(output)
        assert parsed["version"] == "2.1.0"
        assert "$schema" in parsed
        assert "runs" in parsed
        assert len(parsed["runs"]) == 1

    def test_sarif_with_findings(self) -> None:
        """Test SARIF output with findings."""
        result = GovernanceResult(
            spec_path="openapi.yaml",
            policy_name="test",
            status="WARN",
            findings=[
                Finding(
                    rule_id="NAME001",
                    severity=Severity.MINOR,
                    message="Use snake_case for properties",
                    path="/users.get",
                    recommendation="Rename to snake_case",
                )
            ],
        )

        formatter = SARIFFormatter(result)
        sarif = formatter.to_sarif()

        run = sarif["runs"][0]
        assert len(run["tool"]["driver"]["rules"]) == 1
        assert len(run["results"]) == 1
        assert run["results"][0]["level"] == "warning"

    def test_severity_mapping(self) -> None:
        """Test severity to SARIF level mapping."""
        result = GovernanceResult(
            spec_path="openapi.yaml",
            policy_name="test",
            status="FAIL",
            findings=[
                Finding(rule_id="A", severity=Severity.BLOCKER, message="blocker"),
                Finding(rule_id="B", severity=Severity.MAJOR, message="major"),
                Finding(rule_id="C", severity=Severity.MINOR, message="minor"),
                Finding(rule_id="D", severity=Severity.INFO, message="info"),
            ],
        )

        formatter = SARIFFormatter(result)
        sarif = formatter.to_sarif()

        results = sarif["runs"][0]["results"]
        levels = [r["level"] for r in results]
        assert levels == ["error", "error", "warning", "note"]

    def test_write_to_file(self, tmp_path: Path) -> None:
        """Test writing SARIF to file."""
        result = GovernanceResult(
            spec_path="openapi.yaml",
            policy_name="test",
            status="PASS",
        )

        formatter = SARIFFormatter(result)
        path = formatter.write(tmp_path)

        assert path.exists()
        assert path.name == "api-governor-report.sarif"
