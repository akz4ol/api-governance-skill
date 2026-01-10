"""Tests for plugin system."""

from pathlib import Path

import yaml

from api_governor.models import PolicyConfig
from api_governor.parser import OpenAPIParser
from api_governor.plugins import (
    MaxPathDepthRule,
    PluginManager,
    RequireDescriptionRule,
)


class TestPluginManager:
    """Tests for PluginManager class."""

    def test_register_plugin(self) -> None:
        """Test registering a plugin."""
        manager = PluginManager()
        manager.register(RequireDescriptionRule)

        assert len(manager.plugins) == 1
        assert manager.plugins[0].rule_id == "CUSTOM_REQUIRE_DESCRIPTION"

    def test_get_plugin(self) -> None:
        """Test getting plugin by ID."""
        manager = PluginManager()
        manager.register(RequireDescriptionRule)

        plugin = manager.get_plugin("CUSTOM_REQUIRE_DESCRIPTION")
        assert plugin is not None
        assert plugin.name == "Require Operation Description"

    def test_get_nonexistent_plugin(self) -> None:
        """Test getting nonexistent plugin."""
        manager = PluginManager()
        plugin = manager.get_plugin("NONEXISTENT")
        assert plugin is None

    def test_load_from_file(self, tmp_path: Path) -> None:
        """Test loading plugins from file."""
        plugin_code = """
from api_governor.plugins import RulePlugin
from api_governor.models import Finding, Severity

class CustomTestRule(RulePlugin):
    @property
    def rule_id(self):
        return "TEST_RULE"

    @property
    def name(self):
        return "Test Rule"

    @property
    def description(self):
        return "A test rule"

    def check(self, spec, policy):
        return []
"""
        plugin_file = tmp_path / "test_plugin.py"
        plugin_file.write_text(plugin_code)

        manager = PluginManager()
        manager.load_from_file(plugin_file)

        assert len(manager.plugins) == 1
        assert manager.plugins[0].rule_id == "TEST_RULE"


class TestRequireDescriptionRule:
    """Tests for RequireDescriptionRule."""

    def test_finds_missing_description(self, tmp_path: Path) -> None:
        """Test detecting missing operation description."""
        spec_content = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {"/users": {"get": {"responses": {"200": {"description": "OK"}}}}},
        }

        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text(yaml.dump(spec_content))

        parser = OpenAPIParser(spec_file)
        parser.parse()

        policy = PolicyConfig.from_dict({})
        rule = RequireDescriptionRule()
        findings = rule.check(parser, policy)

        assert len(findings) == 1
        assert "missing description" in findings[0].message.lower()

    def test_passes_with_description(self, tmp_path: Path) -> None:
        """Test passing when description present."""
        spec_content = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {
                "/users": {
                    "get": {
                        "description": "Get all users",
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        }

        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text(yaml.dump(spec_content))

        parser = OpenAPIParser(spec_file)
        parser.parse()

        policy = PolicyConfig.from_dict({})
        rule = RequireDescriptionRule()
        findings = rule.check(parser, policy)

        assert len(findings) == 0


class TestMaxPathDepthRule:
    """Tests for MaxPathDepthRule."""

    def test_finds_deep_paths(self, tmp_path: Path) -> None:
        """Test detecting paths exceeding max depth."""
        spec_content = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {"/a/b/c/d/e/f/g": {"get": {"responses": {"200": {"description": "OK"}}}}},
        }

        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text(yaml.dump(spec_content))

        parser = OpenAPIParser(spec_file)
        parser.parse()

        policy = PolicyConfig.from_dict({"custom_rules": {"max_path_depth": 5}})
        rule = MaxPathDepthRule()
        findings = rule.check(parser, policy)

        assert len(findings) == 1
        assert "exceeds max depth" in findings[0].message.lower()

    def test_passes_shallow_paths(self, tmp_path: Path) -> None:
        """Test passing for shallow paths."""
        spec_content = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {"/users/{id}": {"get": {"responses": {"200": {"description": "OK"}}}}},
        }

        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text(yaml.dump(spec_content))

        parser = OpenAPIParser(spec_file)
        parser.parse()

        policy = PolicyConfig.from_dict({})
        rule = MaxPathDepthRule()
        findings = rule.check(parser, policy)

        assert len(findings) == 0
