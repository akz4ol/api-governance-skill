"""Custom rule plugin system for API Governor."""

import importlib.util
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .models import Finding, PolicyConfig, Severity
from .parser import OpenAPIParser


class RulePlugin(ABC):
    """Base class for custom rule plugins."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique rule identifier (e.g., 'CUSTOM001')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable rule name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Rule description."""
        pass

    @property
    def default_severity(self) -> Severity:
        """Default severity for findings from this rule."""
        return Severity.MINOR

    @abstractmethod
    def check(
        self, spec: OpenAPIParser, policy: PolicyConfig
    ) -> list[Finding]:
        """Run the rule check on the spec.

        Args:
            spec: Parsed OpenAPI specification
            policy: Policy configuration

        Returns:
            List of findings (empty if rule passes)
        """
        pass


class PluginManager:
    """Manages loading and running custom rule plugins."""

    def __init__(self) -> None:
        """Initialize plugin manager."""
        self._plugins: list[RulePlugin] = []
        self._builtin_plugins: list[type[RulePlugin]] = []

    def register(self, plugin_class: type[RulePlugin]) -> None:
        """Register a plugin class.

        Args:
            plugin_class: Plugin class to register
        """
        plugin = plugin_class()
        self._plugins.append(plugin)

    def load_from_file(self, plugin_path: str | Path) -> None:
        """Load plugins from a Python file.

        Args:
            plugin_path: Path to Python file containing plugin classes
        """
        path = Path(plugin_path)
        if not path.exists():
            raise FileNotFoundError(f"Plugin file not found: {path}")

        # Load module from file
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to load plugin: {path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)

        # Find all RulePlugin subclasses in module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, RulePlugin)
                and attr is not RulePlugin
            ):
                self.register(attr)

    def load_from_directory(self, plugin_dir: str | Path) -> None:
        """Load all plugins from a directory.

        Args:
            plugin_dir: Directory containing plugin Python files
        """
        path = Path(plugin_dir)
        if not path.is_dir():
            return

        for plugin_file in path.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            try:
                self.load_from_file(plugin_file)
            except Exception as e:
                print(f"Warning: Failed to load plugin {plugin_file}: {e}")

    def run_all(
        self, spec: OpenAPIParser, policy: PolicyConfig
    ) -> list[Finding]:
        """Run all registered plugins.

        Args:
            spec: Parsed OpenAPI specification
            policy: Policy configuration

        Returns:
            Combined list of findings from all plugins
        """
        findings: list[Finding] = []

        for plugin in self._plugins:
            try:
                plugin_findings = plugin.check(spec, policy)
                findings.extend(plugin_findings)
            except Exception as e:
                # Add error as a finding
                findings.append(
                    Finding(
                        rule_id=f"PLUGIN_ERROR_{plugin.rule_id}",
                        severity=Severity.INFO,
                        message=f"Plugin {plugin.name} failed: {e}",
                    )
                )

        return findings

    @property
    def plugins(self) -> list[RulePlugin]:
        """Get all registered plugins."""
        return self._plugins.copy()

    def get_plugin(self, rule_id: str) -> RulePlugin | None:
        """Get plugin by rule ID.

        Args:
            rule_id: Rule identifier

        Returns:
            Plugin instance or None if not found
        """
        for plugin in self._plugins:
            if plugin.rule_id == rule_id:
                return plugin
        return None


# Example built-in plugins


class RequireDescriptionRule(RulePlugin):
    """Ensures all operations have descriptions."""

    @property
    def rule_id(self) -> str:
        return "CUSTOM_REQUIRE_DESCRIPTION"

    @property
    def name(self) -> str:
        return "Require Operation Description"

    @property
    def description(self) -> str:
        return "All API operations should have a description for documentation"

    @property
    def default_severity(self) -> Severity:
        return Severity.MINOR

    def check(
        self, spec: OpenAPIParser, policy: PolicyConfig
    ) -> list[Finding]:
        findings: list[Finding] = []

        for path, method, operation in spec.get_operations():
            if not operation.get("description"):
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity=self.default_severity,
                        message=f"Operation {method.upper()} {path} missing description",
                        path=f"{path}.{method}",
                        recommendation="Add a description field to document the operation",
                    )
                )

        return findings


class RequireExamplesRule(RulePlugin):
    """Ensures request/response schemas have examples."""

    @property
    def rule_id(self) -> str:
        return "CUSTOM_REQUIRE_EXAMPLES"

    @property
    def name(self) -> str:
        return "Require Schema Examples"

    @property
    def description(self) -> str:
        return "Request and response schemas should include examples"

    @property
    def default_severity(self) -> Severity:
        return Severity.INFO

    def check(
        self, spec: OpenAPIParser, policy: PolicyConfig
    ) -> list[Finding]:
        findings: list[Finding] = []

        for path, method, operation in spec.get_operations():
            # Check request body
            request_body = operation.get("requestBody", {})
            content = request_body.get("content", {})
            for media_type, schema_data in content.items():
                schema = schema_data.get("schema", {})
                if not schema_data.get("example") and not schema.get("example"):
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            severity=self.default_severity,
                            message=f"Request body missing example: {method.upper()} {path}",
                            path=f"{path}.{method}.requestBody",
                            recommendation="Add an example to the request body schema",
                        )
                    )

            # Check responses
            for status_code, response in operation.get("responses", {}).items():
                response_content = response.get("content", {})
                for media_type, schema_data in response_content.items():
                    schema = schema_data.get("schema", {})
                    if not schema_data.get("example") and not schema.get("example"):
                        findings.append(
                            Finding(
                                rule_id=self.rule_id,
                                severity=self.default_severity,
                                message=f"Response {status_code} missing example: {method.upper()} {path}",
                                path=f"{path}.{method}.responses.{status_code}",
                                recommendation="Add an example to the response schema",
                            )
                        )

        return findings


class MaxPathDepthRule(RulePlugin):
    """Enforces maximum path depth."""

    @property
    def rule_id(self) -> str:
        return "CUSTOM_MAX_PATH_DEPTH"

    @property
    def name(self) -> str:
        return "Maximum Path Depth"

    @property
    def description(self) -> str:
        return "API paths should not exceed a maximum depth for simplicity"

    @property
    def default_severity(self) -> Severity:
        return Severity.MINOR

    def check(
        self, spec: OpenAPIParser, policy: PolicyConfig
    ) -> list[Finding]:
        findings: list[Finding] = []
        max_depth = policy.get("custom_rules.max_path_depth", 5)

        for path in spec.paths.keys():
            # Count path segments (excluding empty strings from leading/trailing slashes)
            segments = [s for s in path.split("/") if s]
            if len(segments) > max_depth:
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        severity=self.default_severity,
                        message=f"Path exceeds max depth of {max_depth}: {path}",
                        path=path,
                        recommendation=f"Consider flattening the path structure to max {max_depth} segments",
                    )
                )

        return findings


# Default plugin manager instance
default_manager = PluginManager()

# Register built-in plugins
default_manager.register(RequireDescriptionRule)
default_manager.register(RequireExamplesRule)
default_manager.register(MaxPathDepthRule)
