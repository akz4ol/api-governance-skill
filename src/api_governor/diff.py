"""OpenAPI spec differ for breaking change detection."""

from .models import BreakingChange, PolicyConfig, Severity
from .parser import OpenAPIParser


class SpecDiffer:
    """Detects breaking changes between OpenAPI spec versions."""

    def __init__(self, policy: PolicyConfig):
        """Initialize with policy configuration."""
        self.policy = policy

    def diff(self, baseline: OpenAPIParser, current: OpenAPIParser) -> list[BreakingChange]:
        """Find breaking changes between baseline and current spec."""
        changes: list[BreakingChange] = []

        if self.policy.get("breaking_change_detection.enabled", True):
            changes.extend(self._check_removed_operations(baseline, current))
            changes.extend(self._check_removed_parameters(baseline, current))
            changes.extend(self._check_response_changes(baseline, current))
            changes.extend(self._check_schema_changes(baseline, current))

        return changes

    def _get_default_severity(self) -> Severity:
        """Get default severity for breaking changes."""
        level = self.policy.get("breaking_change_detection.default_breaking_severity", "MAJOR")
        return Severity[level]

    def _check_removed_operations(
        self, baseline: OpenAPIParser, current: OpenAPIParser
    ) -> list[BreakingChange]:
        """Check for removed operations."""
        changes: list[BreakingChange] = []

        if not self.policy.get(
            "breaking_change_detection.breaking_changes.removed_operation", True
        ):
            return changes

        baseline_ops = {(p, m) for p, m, _ in baseline.get_operations()}
        current_ops = {(p, m) for p, m, _ in current.get_operations()}

        removed = baseline_ops - current_ops
        for path, method in removed:
            changes.append(
                BreakingChange(
                    change_type="removed_operation",
                    path=f"{method.upper()} {path}",
                    description=f"Operation removed: {method.upper()} {path}",
                    client_impact="Clients calling this endpoint will receive 404 errors",
                    severity=self._get_default_severity(),
                )
            )

        return changes

    def _check_removed_parameters(
        self, baseline: OpenAPIParser, current: OpenAPIParser
    ) -> list[BreakingChange]:
        """Check for removed or renamed parameters."""
        changes: list[BreakingChange] = []

        if not self.policy.get(
            "breaking_change_detection.breaking_changes.removed_parameter", True
        ):
            return changes

        baseline_ops = {(p, m): op for p, m, op in baseline.get_operations()}
        current_ops = {(p, m): op for p, m, op in current.get_operations()}

        for (path, method), baseline_op in baseline_ops.items():
            if (path, method) not in current_ops:
                continue

            current_op = current_ops[(path, method)]
            baseline_params = {p.get("name"): p for p in baseline_op.get("parameters", [])}
            current_params = {p.get("name"): p for p in current_op.get("parameters", [])}

            removed_params = set(baseline_params.keys()) - set(current_params.keys())
            for param_name in removed_params:
                changes.append(
                    BreakingChange(
                        change_type="removed_parameter",
                        path=f"{method.upper()} {path} -> {param_name}",
                        description=f"Parameter removed: '{param_name}' from {method.upper()} {path}",
                        client_impact="Clients sending this parameter will have it ignored or may receive errors",
                        severity=self._get_default_severity(),
                    )
                )

        return changes

    def _check_response_changes(
        self, baseline: OpenAPIParser, current: OpenAPIParser
    ) -> list[BreakingChange]:
        """Check for breaking response changes."""
        changes: list[BreakingChange] = []

        baseline_ops = {(p, m): op for p, m, op in baseline.get_operations()}
        current_ops = {(p, m): op for p, m, op in current.get_operations()}

        for (path, method), baseline_op in baseline_ops.items():
            if (path, method) not in current_ops:
                continue

            current_op = current_ops[(path, method)]
            baseline_responses = baseline_op.get("responses", {})
            current_responses = current_op.get("responses", {})

            # Check for removed status codes
            if self.policy.get(
                "breaking_change_detection.breaking_changes.status_code_removed", True
            ):
                removed_codes = set(baseline_responses.keys()) - set(current_responses.keys())
                for code in removed_codes:
                    changes.append(
                        BreakingChange(
                            change_type="removed_status_code",
                            path=f"{method.upper()} {path} -> {code}",
                            description=f"Response status code removed: {code} from {method.upper()} {path}",
                            client_impact="Clients handling this status code may not handle the new response correctly",
                            severity=self._get_default_severity(),
                        )
                    )

        return changes

    def _check_schema_changes(
        self, baseline: OpenAPIParser, current: OpenAPIParser
    ) -> list[BreakingChange]:
        """Check for breaking schema changes."""
        changes: list[BreakingChange] = []

        baseline_schemas = baseline.components.get("schemas", {})
        current_schemas = current.components.get("schemas", {})

        for schema_name, baseline_schema in baseline_schemas.items():
            if schema_name not in current_schemas:
                continue

            current_schema = current_schemas[schema_name]

            # Check for removed fields
            if self.policy.get(
                "breaking_change_detection.breaking_changes.removed_response_field", True
            ):
                baseline_props = set(baseline_schema.get("properties", {}).keys())
                current_props = set(current_schema.get("properties", {}).keys())

                removed_props = baseline_props - current_props
                for prop in removed_props:
                    changes.append(
                        BreakingChange(
                            change_type="removed_field",
                            path=f"schemas.{schema_name}.{prop}",
                            description=f"Field removed: '{prop}' from schema '{schema_name}'",
                            client_impact="Clients expecting this field will receive null/undefined or fail parsing",
                            severity=self._get_default_severity(),
                        )
                    )

            # Check for optional-to-required flips
            if self.policy.get(
                "breaking_change_detection.breaking_changes.optional_to_required_flip", True
            ):
                baseline_required = set(baseline_schema.get("required", []))
                current_required = set(current_schema.get("required", []))

                new_required = current_required - baseline_required
                for prop in new_required:
                    if prop in baseline_schema.get("properties", {}):
                        changes.append(
                            BreakingChange(
                                change_type="optional_to_required",
                                path=f"schemas.{schema_name}.{prop}",
                                description=f"Field changed from optional to required: '{prop}' in '{schema_name}'",
                                client_impact="Clients not providing this field will receive validation errors",
                                severity=self._get_default_severity(),
                            )
                        )

        return changes
