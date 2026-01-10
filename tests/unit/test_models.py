"""Tests for data models."""

from api_governor.models import BreakingChange, Finding, GovernanceResult, Severity


class TestFinding:
    """Tests for Finding model."""

    def test_to_dict(self) -> None:
        """Test converting Finding to dict."""
        finding = Finding(
            rule_id="SEC001",
            severity=Severity.MAJOR,
            message="Missing security",
            path="paths./users.get",
            recommendation="Add security requirement",
        )

        result = finding.to_dict()

        assert result["rule_id"] == "SEC001"
        assert result["severity"] == "MAJOR"
        assert result["message"] == "Missing security"
        assert result["path"] == "paths./users.get"
        assert result["recommendation"] == "Add security requirement"


class TestGovernanceResult:
    """Tests for GovernanceResult model."""

    def test_severity_filtering(self) -> None:
        """Test filtering findings by severity."""
        findings = [
            Finding("A", Severity.BLOCKER, "blocker1"),
            Finding("B", Severity.MAJOR, "major1"),
            Finding("C", Severity.BLOCKER, "blocker2"),
            Finding("D", Severity.MINOR, "minor1"),
            Finding("E", Severity.INFO, "info1"),
        ]

        result = GovernanceResult(
            spec_path="test.yaml",
            policy_name="Test",
            status="FAIL",
            findings=findings,
        )

        assert len(result.blockers) == 2
        assert len(result.majors) == 1
        assert len(result.minors) == 1
        assert len(result.infos) == 1


class TestBreakingChange:
    """Tests for BreakingChange model."""

    def test_to_dict(self) -> None:
        """Test converting BreakingChange to dict."""
        change = BreakingChange(
            change_type="removed_operation",
            path="DELETE /users/{id}",
            description="Operation removed",
            client_impact="Clients will get 404",
            severity=Severity.MAJOR,
        )

        result = change.to_dict()

        assert result["change_type"] == "removed_operation"
        assert result["severity"] == "MAJOR"
