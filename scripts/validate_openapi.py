#!/usr/bin/env python3
"""Validate OpenAPI spec files."""

import sys
from pathlib import Path

import yaml


def validate_openapi(spec_path: Path) -> list[str]:
    """Validate an OpenAPI spec file."""
    errors = []

    try:
        with open(spec_path) as f:
            spec = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(spec, dict):
        return ["Spec must be a YAML/JSON object"]

    # Check for OpenAPI version
    openapi_version = spec.get("openapi") or spec.get("swagger")
    if not openapi_version:
        errors.append("Missing 'openapi' or 'swagger' version field")

    # Check for info
    if "info" not in spec:
        errors.append("Missing 'info' section")
    else:
        info = spec["info"]
        if "title" not in info:
            errors.append("Missing 'info.title'")
        if "version" not in info:
            errors.append("Missing 'info.version'")

    # Check for paths
    if "paths" not in spec:
        errors.append("Missing 'paths' section")

    # Basic $ref validation
    def check_refs(obj: dict | list, path: str = "") -> None:
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                if not ref.startswith("#/"):
                    errors.append(f"External ref not supported at {path}: {ref}")
                else:
                    # Try to resolve internal ref
                    ref_parts = ref[2:].split("/")
                    target = spec
                    for part in ref_parts:
                        if isinstance(target, dict) and part in target:
                            target = target[part]
                        else:
                            errors.append(f"Unresolved ref at {path}: {ref}")
                            break
            for key, value in obj.items():
                check_refs(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_refs(item, f"{path}[{i}]")

    check_refs(spec)

    return errors


def main() -> int:
    """Validate OpenAPI spec files passed as arguments."""
    if len(sys.argv) < 2:
        print("Usage: validate_openapi.py <spec1.yaml> [spec2.yaml ...]")
        return 1

    all_errors = []
    for spec_path_str in sys.argv[1:]:
        spec_path = Path(spec_path_str)
        if not spec_path.exists():
            print(f"File not found: {spec_path}")
            all_errors.append((spec_path.name, ["File not found"]))
            continue

        print(f"Validating {spec_path.name}...")
        errors = validate_openapi(spec_path)

        if errors:
            print(f"  ✗ {len(errors)} error(s):")
            for error in errors:
                print(f"    - {error}")
            all_errors.append((spec_path.name, errors))
        else:
            print(f"  ✓ Valid")

    print()
    if all_errors:
        print(f"Validation failed: {len(all_errors)} file(s) with errors")
        return 1

    print(f"All {len(sys.argv) - 1} spec files are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
