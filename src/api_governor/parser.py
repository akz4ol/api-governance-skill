"""OpenAPI spec parser."""

from pathlib import Path
from typing import Any, cast

import yaml


class OpenAPIParseError(Exception):
    """Error parsing OpenAPI spec."""

    pass


class OpenAPIParser:
    """Parser for OpenAPI specifications."""

    def __init__(self, spec_path: str | Path):
        """Initialize parser with spec path."""
        self.spec_path = Path(spec_path)
        self._spec: dict[str, Any] | None = None

    def parse(self) -> dict[str, Any]:
        """Parse the OpenAPI spec file."""
        if self._spec is not None:
            return self._spec

        if not self.spec_path.exists():
            raise OpenAPIParseError(f"Spec file not found: {self.spec_path}")

        try:
            content = self.spec_path.read_text()
            if self.spec_path.suffix in (".yaml", ".yml"):
                self._spec = yaml.safe_load(content)
            elif self.spec_path.suffix == ".json":
                import json

                self._spec = json.loads(content)
            else:
                # Try YAML first, then JSON
                try:
                    self._spec = yaml.safe_load(content)
                except yaml.YAMLError:
                    import json

                    self._spec = json.loads(content)
        except Exception as e:
            raise OpenAPIParseError(f"Failed to parse {self.spec_path}: {e}") from e

        if self._spec is None:
            raise OpenAPIParseError(f"Failed to parse {self.spec_path}: empty or invalid content")
        return self._spec

    @property
    def spec(self) -> dict[str, Any]:
        """Get parsed spec."""
        if self._spec is None:
            self.parse()
        assert self._spec is not None
        return self._spec

    @property
    def version(self) -> str:
        """Get OpenAPI version."""
        return cast(str, self.spec.get("openapi", self.spec.get("swagger", "unknown")))

    @property
    def info(self) -> dict[str, Any]:
        """Get API info."""
        return cast(dict[str, Any], self.spec.get("info", {}))

    @property
    def paths(self) -> dict[str, Any]:
        """Get API paths."""
        return cast(dict[str, Any], self.spec.get("paths", {}))

    @property
    def components(self) -> dict[str, Any]:
        """Get components/definitions."""
        return cast(dict[str, Any], self.spec.get("components", self.spec.get("definitions", {})))

    @property
    def security(self) -> list[dict[str, Any]]:
        """Get global security requirements."""
        return cast(list[dict[str, Any]], self.spec.get("security", []))

    def get_operations(self) -> list[tuple[str, str, dict[str, Any]]]:
        """Get all operations as (path, method, operation) tuples."""
        operations = []
        for path, path_item in self.paths.items():
            for method in ("get", "post", "put", "patch", "delete", "options", "head"):
                if method in path_item:
                    operations.append((path, method, path_item[method]))
        return operations

    def resolve_ref(self, ref: str) -> dict[str, Any]:
        """Resolve a $ref reference."""
        if not ref.startswith("#/"):
            raise OpenAPIParseError(f"External refs not supported: {ref}")

        parts = ref[2:].split("/")
        value = self.spec
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, {})
            else:
                return {}
        return value

    def validate_refs(self) -> list[str]:
        """Validate all internal references are resolvable."""
        errors = []

        def check_refs(obj: Any, path: str = "") -> None:
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref = obj["$ref"]
                    try:
                        resolved = self.resolve_ref(ref)
                        if not resolved:
                            errors.append(f"Unresolved ref at {path}: {ref}")
                    except OpenAPIParseError as e:
                        errors.append(f"Invalid ref at {path}: {e}")
                for key, value in obj.items():
                    check_refs(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_refs(item, f"{path}[{i}]")

        check_refs(self.spec)
        return errors
