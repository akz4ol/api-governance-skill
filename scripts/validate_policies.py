#!/usr/bin/env python3
"""Validate policy YAML files against the JSON schema."""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import ValidationError, validate


def main() -> int:
    """Validate all policy files."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    schema_path = repo_root / "schemas" / "policy.schema.json"
    policy_dir = repo_root / "skills" / "api-governor" / "policy"

    if not schema_path.exists():
        print(f"Error: Schema not found at {schema_path}")
        return 1

    with open(schema_path) as f:
        schema = json.load(f)

    policy_files = list(policy_dir.glob("*.yaml")) + list(policy_dir.glob("*.yml"))

    if not policy_files:
        print(f"Warning: No policy files found in {policy_dir}")
        return 0

    errors = []
    for policy_path in policy_files:
        print(f"Validating {policy_path.name}...")
        try:
            with open(policy_path) as f:
                policy = yaml.safe_load(f)

            validate(instance=policy, schema=schema)
            print("  ✓ Valid")
        except ValidationError as e:
            print(f"  ✗ Invalid: {e.message}")
            errors.append((policy_path.name, e.message))
        except yaml.YAMLError as e:
            print(f"  ✗ YAML error: {e}")
            errors.append((policy_path.name, str(e)))

    print()
    if errors:
        print(f"Validation failed: {len(errors)} error(s)")
        for filename, error in errors:
            print(f"  - {filename}: {error}")
        return 1

    print(f"All {len(policy_files)} policy files are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
