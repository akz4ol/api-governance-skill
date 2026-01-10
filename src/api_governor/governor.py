"""Main API Governor orchestrator."""

from pathlib import Path

import yaml

from .diff import SpecDiffer
from .models import Finding, GovernanceResult, PolicyConfig, Severity
from .output import OutputGenerator
from .parser import OpenAPIParseError, OpenAPIParser
from .rules import RuleEngine


class APIGovernor:
    """Main API governance orchestrator."""

    def __init__(
        self,
        spec_path: str | Path,
        policy_path: str | Path | None = None,
        baseline_path: str | Path | None = None,
        output_dir: str | Path = "governance",
    ):
        """Initialize API Governor.

        Args:
            spec_path: Path to OpenAPI spec to analyze
            policy_path: Path to policy YAML file (optional, uses default)
            baseline_path: Path to baseline spec for breaking change detection
            output_dir: Directory for output artifacts
        """
        self.spec_path = Path(spec_path)
        self.policy_path = Path(policy_path) if policy_path else self._get_default_policy()
        self.baseline_path = Path(baseline_path) if baseline_path else None
        self.output_dir = Path(output_dir)

        self._policy: PolicyConfig | None = None
        self._parser: OpenAPIParser | None = None
        self._baseline_parser: OpenAPIParser | None = None

    def _get_default_policy(self) -> Path:
        """Get path to default policy file."""
        skill_dir = Path(__file__).parent.parent.parent
        return skill_dir / "skills" / "api-governor" / "policy" / "default.internal.yaml"

    def _load_policy(self) -> PolicyConfig:
        """Load policy configuration."""
        if self._policy is not None:
            return self._policy

        if not self.policy_path.exists():
            raise FileNotFoundError(f"Policy file not found: {self.policy_path}")

        with open(self.policy_path) as f:
            data = yaml.safe_load(f)

        self._policy = PolicyConfig.from_dict(data)
        return self._policy

    def run(self) -> GovernanceResult:
        """Run governance analysis.

        Returns:
            GovernanceResult with findings and recommendations
        """
        policy = self._load_policy()
        findings: list[Finding] = []
        checklist: dict[str, bool] = {}

        # Step 1: Parse spec
        try:
            self._parser = OpenAPIParser(self.spec_path)
            self._parser.parse()
            checklist["OpenAPI parseable"] = True
        except OpenAPIParseError as e:
            findings.append(
                Finding(
                    rule_id="PARSE001",
                    severity=Severity.BLOCKER,
                    message=f"Failed to parse OpenAPI spec: {e}",
                    path=str(self.spec_path),
                    recommendation="Fix the spec syntax and try again",
                )
            )
            return GovernanceResult(
                spec_path=str(self.spec_path),
                policy_name=policy.name,
                status="FAIL",
                findings=findings,
                checklist=checklist,
            )

        # Step 2: Validate refs
        ref_errors = self._parser.validate_refs()
        if ref_errors:
            for error in ref_errors:
                findings.append(
                    Finding(
                        rule_id="REF001",
                        severity=Severity.BLOCKER,
                        message=error,
                        recommendation="Fix unresolved $ref references",
                    )
                )

        # Step 3: Apply governance rules
        rule_engine = RuleEngine(policy)
        findings.extend(rule_engine.evaluate(self._parser))

        # Update checklist based on findings
        checklist["Standard error envelope present"] = not any(
            f.rule_id.startswith("ERR") for f in findings
        )
        checklist["Security declared globally"] = bool(self._parser.security)
        checklist["Pagination conforms to policy"] = not any(
            f.rule_id.startswith("PAG") for f in findings
        )

        # Step 4: Breaking change detection
        breaking_changes = []
        if self.baseline_path and self.baseline_path.exists():
            self._baseline_parser = OpenAPIParser(self.baseline_path)
            try:
                self._baseline_parser.parse()
                differ = SpecDiffer(policy)
                breaking_changes = differ.diff(self._baseline_parser, self._parser)

                # Escalate breaking changes to findings if no deprecation plan
                escalate = policy.get(
                    "breaking_change_detection.escalate_to_blocker_if.no_deprecation_plan", True
                )
                if breaking_changes and escalate:
                    findings.append(
                        Finding(
                            rule_id="BREAK001",
                            severity=Severity.BLOCKER,
                            message=f"Breaking changes detected ({len(breaking_changes)}) without deprecation plan",
                            recommendation="Create DEPRECATION_PLAN.md or revert breaking changes",
                        )
                    )

                checklist["Breaking changes accompanied by deprecation plan"] = not breaking_changes
            except OpenAPIParseError:
                pass  # Baseline parse errors are non-fatal

        # Determine overall status
        has_blockers = any(f.severity == Severity.BLOCKER for f in findings)
        has_majors = any(f.severity == Severity.MAJOR for f in findings)

        if has_blockers:
            status = "FAIL"
        elif has_majors:
            status = "WARN"
        else:
            status = "PASS"

        result = GovernanceResult(
            spec_path=str(self.spec_path),
            policy_name=policy.name,
            status=status,
            findings=findings,
            breaking_changes=breaking_changes,
            checklist=checklist,
        )

        return result

    def generate_artifacts(self, result: GovernanceResult | None = None) -> dict[str, Path]:
        """Generate output artifacts.

        Args:
            result: GovernanceResult (runs analysis if not provided)

        Returns:
            Dict mapping artifact names to file paths
        """
        if result is None:
            result = self.run()

        self.output_dir.mkdir(parents=True, exist_ok=True)
        policy = self._load_policy()

        generator = OutputGenerator(result, policy, self.output_dir)
        return generator.generate_all()
