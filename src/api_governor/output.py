"""Output artifact generators."""

from pathlib import Path

from .models import GovernanceResult, PolicyConfig, Severity


class OutputGenerator:
    """Generates governance output artifacts."""

    def __init__(
        self,
        result: GovernanceResult,
        policy: PolicyConfig,
        output_dir: Path,
    ):
        """Initialize output generator."""
        self.result = result
        self.policy = policy
        self.output_dir = output_dir

    def generate_all(self) -> dict[str, Path]:
        """Generate all applicable artifacts."""
        artifacts = {}

        # Always generate API_REVIEW.md
        review_path = self._generate_review()
        artifacts["API_REVIEW.md"] = review_path

        # Generate changelog if there are breaking changes
        if self.result.breaking_changes:
            changelog_path = self._generate_changelog()
            artifacts["API_CHANGELOG.md"] = changelog_path

            deprecation_path = self._generate_deprecation_plan()
            artifacts["DEPRECATION_PLAN.md"] = deprecation_path

        return artifacts

    def _generate_review(self) -> Path:
        """Generate API_REVIEW.md."""
        lines = [
            "# API Review (API Governor)",
            "",
            "## Summary",
            f"**Result:** {self.result.status}",
            f"**Policy:** {self.policy.name} v{self.policy.version}",
            f"**Spec:** {self.result.spec_path}",
            "",
        ]

        # Findings by severity
        for severity in [Severity.BLOCKER, Severity.MAJOR, Severity.MINOR, Severity.INFO]:
            findings = [f for f in self.result.findings if f.severity == severity]
            if findings:
                lines.append(f"## {severity.value} Findings")
                for i, f in enumerate(findings, 1):
                    lines.append(f"{i}) **{f.message}**")
                    if f.path:
                        lines.append(f"   - Path: `{f.path}`")
                    if f.recommendation:
                        lines.append(f"   - Recommended fix: {f.recommendation}")
                    lines.append("")

        # Checklist
        lines.append("## Checklist")
        for item, passed in self.result.checklist.items():
            check = "x" if passed else " "
            lines.append(f"- [{check}] {item}")
        lines.append("")

        # Next steps
        if self.result.status != "PASS":
            lines.append("## Next Steps")
            if self.result.blockers:
                lines.append("- Address BLOCKER findings before merging")
            if self.result.breaking_changes:
                lines.append("- Create `DEPRECATION_PLAN.md` for breaking changes")
                lines.append("- Consider reverting breaking changes if migration is not planned")
            lines.append("")

        content = "\n".join(lines)
        path = self.output_dir / "API_REVIEW.md"
        path.write_text(content)
        return path

    def _generate_changelog(self) -> Path:
        """Generate API_CHANGELOG.md."""
        lines = [
            "# API Changelog (Spec Diff)",
            "",
        ]

        breaking = list(self.result.breaking_changes)

        lines.append("## Breaking Changes")
        if breaking:
            for bc in breaking:
                lines.append(f"- **{bc.change_type}**: {bc.description}")
                lines.append(f"  - Client impact: {bc.client_impact}")
        else:
            lines.append("- None detected.")
        lines.append("")

        lines.append("## Non-breaking Changes")
        lines.append("- Analysis pending (manual review recommended)")
        lines.append("")

        lines.append("## Deprecations Introduced")
        lines.append("- Check spec for `deprecated: true` markers")
        lines.append("")

        content = "\n".join(lines)
        path = self.output_dir / "API_CHANGELOG.md"
        path.write_text(content)
        return path

    def _generate_deprecation_plan(self) -> Path:
        """Generate DEPRECATION_PLAN.md."""
        lines = [
            "# Deprecation & Migration Plan",
            "",
            "## Overview",
            "Breaking changes detected requiring migration planning.",
            "",
            "## Breaking Changes Summary",
        ]

        for bc in self.result.breaking_changes:
            lines.append(f"- **{bc.path}**: {bc.description}")
        lines.append("")

        lines.append("## Migration Strategy (Recommended)")
        lines.append("")
        lines.append("**Option A (Backward Compatible):**")
        lines.append("- Revert breaking changes")
        lines.append("- Add new fields/endpoints alongside existing ones")
        lines.append("- Mark old fields/endpoints as deprecated")
        lines.append("")
        lines.append("**Option B (Versioned Endpoint):**")
        lines.append("- Keep current behavior on existing paths")
        lines.append("- Introduce new version (e.g., /v2/) with breaking changes")
        lines.append("- Publish migration guide")
        lines.append("")

        lines.append("## Timeline")
        lines.append("- Week 0: Announce deprecation and publish migration notes")
        lines.append("- Week 2: Provide compatibility layer or dual support")
        lines.append("- Week 6: Sunset old behavior (only if all known clients migrated)")
        lines.append("")

        lines.append("## Client Migration Notes")
        for bc in self.result.breaking_changes:
            lines.append(f"- {bc.client_impact}")
        lines.append("")

        lines.append("## Communication Template")
        lines.append("```")
        lines.append("Subject: Upcoming API Breaking Changes")
        lines.append("")
        lines.append("We're introducing changes that may affect your integration.")
        lines.append("Please review the migration guide and update by <date>.")
        lines.append("")
        lines.append("Details: <link>")
        lines.append("```")
        lines.append("")

        content = "\n".join(lines)
        path = self.output_dir / "DEPRECATION_PLAN.md"
        path.write_text(content)
        return path
