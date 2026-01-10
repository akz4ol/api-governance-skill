"""Governance rule engine."""

from collections.abc import Callable

from .models import Finding, PolicyConfig, Severity
from .parser import OpenAPIParser


class RuleEngine:
    """Engine for evaluating governance rules against OpenAPI specs."""

    def __init__(self, policy: PolicyConfig):
        """Initialize with policy configuration."""
        self.policy = policy
        self._rules: list[Callable[[OpenAPIParser], list[Finding]]] = []
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default governance rules."""
        self._rules.extend(
            [
                self._check_security,
                self._check_error_envelope,
                self._check_pagination,
                self._check_naming,
                self._check_observability,
                self._check_versioning,
            ]
        )

    def evaluate(self, parser: OpenAPIParser) -> list[Finding]:
        """Evaluate all rules against the spec."""
        findings: list[Finding] = []
        for rule in self._rules:
            findings.extend(rule(parser))
        return findings

    def _check_security(self, parser: OpenAPIParser) -> list[Finding]:
        """Check security requirements."""
        findings: list[Finding] = []
        require_security = self.policy.get("security.require_security_by_default", True)
        allow_public = self.policy.get("security.allow_public_endpoints_if.explicitly_marked", True)
        _public_marker = self.policy.get(
            "security.allow_public_endpoints_if.marker", "x-public: true"
        )  # noqa: F841
        severity = Severity[
            self.policy.get("enforcement.default_severity.security_missing", "MAJOR")
        ]

        if not require_security:
            return findings

        global_security = parser.security

        for path, method, operation in parser.get_operations():
            op_security = operation.get("security", global_security)
            is_public = operation.get("x-public", False)

            if not op_security and not (allow_public and is_public):
                findings.append(
                    Finding(
                        rule_id="SEC001",
                        severity=severity,
                        message=f"Missing security requirement on {method.upper()} {path}",
                        path=f"paths.{path}.{method}",
                        recommendation="Add security requirement or mark as public with x-public: true",
                    )
                )

        return findings

    def _check_error_envelope(self, parser: OpenAPIParser) -> list[Finding]:
        """Check for consistent error envelope."""
        findings: list[Finding] = []
        require_envelope = self.policy.get("errors.require_standard_error_envelope", True)
        envelope_name = self.policy.get("errors.envelope_name", "Error")
        required_fields = self.policy.get(
            "errors.problem_fields_required", ["code", "message", "requestId"]
        )
        severity = Severity[
            self.policy.get("enforcement.default_severity.error_model_inconsistent", "MAJOR")
        ]

        if not require_envelope:
            return findings

        # Check if Error schema exists
        schemas = parser.components.get("schemas", {})
        error_schema = schemas.get(envelope_name)

        if not error_schema:
            findings.append(
                Finding(
                    rule_id="ERR001",
                    severity=severity,
                    message=f"Missing standard error schema '{envelope_name}'",
                    path="components.schemas",
                    recommendation=f"Add {envelope_name} schema with fields: {', '.join(required_fields)}",
                )
            )
            return findings

        # Check required fields
        schema_props = error_schema.get("properties", {})
        _schema_required = error_schema.get("required", [])  # noqa: F841

        for field in required_fields:
            if field not in schema_props:
                findings.append(
                    Finding(
                        rule_id="ERR002",
                        severity=severity,
                        message=f"Error schema missing field: {field}",
                        path=f"components.schemas.{envelope_name}",
                        recommendation=f"Add '{field}' property to {envelope_name} schema",
                    )
                )

        return findings

    def _check_pagination(self, parser: OpenAPIParser) -> list[Finding]:
        """Check pagination conventions."""
        findings: list[Finding] = []
        require_pagination = self.policy.get("pagination.required_for_list_endpoints", True)
        style = self.policy.get("pagination.style", "cursor")
        limit_param = self.policy.get("pagination.request_params.limit", "limit")
        cursor_param = self.policy.get("pagination.request_params.cursor", "cursor")
        _items_field = self.policy.get("pagination.response_shape.items", "items")  # noqa: F841
        _next_cursor_field = self.policy.get("pagination.response_shape.nextCursor", "nextCursor")  # noqa: F841
        severity = Severity[
            self.policy.get("enforcement.default_severity.pagination_inconsistent", "MAJOR")
        ]

        if not require_pagination:
            return findings

        for path, method, operation in parser.get_operations():
            # Check GET endpoints that look like list operations
            if method != "get":
                continue

            # Heuristic: path ends with resource name (not ID pattern)
            if "{" in path.split("/")[-1]:
                continue

            # Check for pagination parameters
            params = {p.get("name"): p for p in operation.get("parameters", [])}

            has_limit = limit_param in params
            has_cursor = cursor_param in params

            if not has_limit:
                findings.append(
                    Finding(
                        rule_id="PAG001",
                        severity=severity,
                        message=f"List endpoint missing '{limit_param}' parameter: {method.upper()} {path}",
                        path=f"paths.{path}.{method}.parameters",
                        recommendation=f"Add '{limit_param}' query parameter for pagination",
                    )
                )

            if style == "cursor" and not has_cursor:
                findings.append(
                    Finding(
                        rule_id="PAG002",
                        severity=severity,
                        message=f"List endpoint missing '{cursor_param}' parameter: {method.upper()} {path}",
                        path=f"paths.{path}.{method}.parameters",
                        recommendation=f"Add '{cursor_param}' query parameter for cursor pagination",
                    )
                )

        return findings

    def _check_naming(self, parser: OpenAPIParser) -> list[Finding]:
        """Check naming conventions."""
        findings: list[Finding] = []
        prefer_kebab = self.policy.get("api_style.prefer_kebab_case_paths", True)
        discourage_verbs = self.policy.get("api_style.discourage_verbs_in_paths", True)
        severity = Severity[
            self.policy.get("enforcement.default_severity.naming_inconsistent", "MINOR")
        ]

        verb_patterns = ["get", "create", "update", "delete", "fetch", "list", "add", "remove"]

        for path in parser.paths.keys():
            # Check kebab-case
            if prefer_kebab:
                segments = path.strip("/").split("/")
                for segment in segments:
                    if "{" in segment:
                        continue
                    if "_" in segment or (segment != segment.lower()):
                        findings.append(
                            Finding(
                                rule_id="NAM001",
                                severity=severity,
                                message=f"Path segment not in kebab-case: '{segment}' in {path}",
                                path=f"paths.{path}",
                                recommendation="Use kebab-case for path segments (lowercase with hyphens)",
                            )
                        )

            # Check for verbs in paths
            if discourage_verbs:
                segments = path.lower().strip("/").split("/")
                for segment in segments:
                    if "{" in segment:
                        continue
                    for verb in verb_patterns:
                        if (
                            segment == verb
                            or segment.startswith(f"{verb}-")
                            or segment.endswith(f"-{verb}")
                        ):
                            findings.append(
                                Finding(
                                    rule_id="NAM002",
                                    severity=severity,
                                    message=f"Verb in path segment: '{segment}' in {path}",
                                    path=f"paths.{path}",
                                    recommendation="Use nouns for resources; HTTP methods convey the action",
                                )
                            )
                            break

        return findings

    def _check_observability(self, parser: OpenAPIParser) -> list[Finding]:
        """Check observability headers."""
        findings: list[Finding] = []
        require_request_id = self.policy.get("observability.require_request_id_header", True)
        _header_name = self.policy.get("observability.header_name", "X-Request-Id")  # noqa: F841
        severity = Severity[
            self.policy.get("enforcement.default_severity.observability_missing", "MINOR")
        ]

        if not require_request_id:
            return findings

        # Check if request ID is in error responses
        schemas = parser.components.get("schemas", {})
        error_schema = schemas.get("Error", {})
        error_props = error_schema.get("properties", {})

        if "requestId" not in error_props:
            findings.append(
                Finding(
                    rule_id="OBS001",
                    severity=severity,
                    message="Error schema missing 'requestId' field for observability",
                    path="components.schemas.Error.properties",
                    recommendation="Add 'requestId' field to Error schema for request tracing",
                )
            )

        return findings

    def _check_versioning(self, parser: OpenAPIParser) -> list[Finding]:
        """Check versioning conventions."""
        findings: list[Finding] = []
        strategy = self.policy.get("versioning.strategy", "none_or_header")
        url_versioning = self.policy.get("versioning.url_versioning.enabled", False)
        severity = Severity[
            self.policy.get("enforcement.default_severity.versioning_inconsistent", "MINOR")
        ]

        if strategy == "url" and url_versioning:
            prefix = self.policy.get("versioning.url_versioning.prefix", "/v{major}")
            # Check if paths have version prefix
            has_versioned_paths = any(p.startswith("/v") for p in parser.paths.keys())
            if not has_versioned_paths:
                findings.append(
                    Finding(
                        rule_id="VER001",
                        severity=severity,
                        message=f"URL versioning required but no versioned paths found (expected prefix: {prefix})",
                        path="paths",
                        recommendation="Add version prefix to paths, e.g., /v1/users",
                    )
                )

        return findings
