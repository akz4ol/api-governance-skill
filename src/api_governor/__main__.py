"""CLI entry point for API Governor."""

import argparse
import json
import sys
from pathlib import Path

from . import APIGovernor, __version__


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="api-governor",
        description="API governance and breaking change detection for OpenAPI specs",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "spec",
        type=Path,
        help="Path to OpenAPI spec file",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        help="Path to policy YAML file (default: pragmatic internal)",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Path to baseline spec for breaking change detection",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("governance"),
        help="Output directory for artifacts (default: governance/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of generating markdown artifacts",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Use strict public API policy preset",
    )

    args = parser.parse_args()

    # Determine policy path
    policy_path = args.policy
    if args.strict and not args.policy:
        skill_dir = Path(__file__).parent.parent.parent
        policy_path = skill_dir / "skills" / "api-governor" / "policy" / "preset.strict.public.yaml"

    try:
        governor = APIGovernor(
            spec_path=args.spec,
            policy_path=policy_path,
            baseline_path=args.baseline,
            output_dir=args.output,
        )

        result = governor.run()

        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            artifacts = governor.generate_artifacts(result)

            print(f"\n{'=' * 60}")
            print(f"API Governance Result: {result.status}")
            print(f"{'=' * 60}")
            print(f"Policy: {result.policy_name}")
            print(f"Spec: {result.spec_path}")
            print()

            print("Findings:")
            print(f"  BLOCKER: {len(result.blockers)}")
            print(f"  MAJOR:   {len(result.majors)}")
            print(f"  MINOR:   {len(result.minors)}")
            print(f"  INFO:    {len(result.infos)}")
            print()

            if result.breaking_changes:
                print(f"Breaking Changes: {len(result.breaking_changes)}")
                print()

            print("Generated Artifacts:")
            for name, path in artifacts.items():
                print(f"  {name}: {path}")
            print()

        # Exit code based on result
        if result.status == "FAIL":
            return 1
        elif result.status == "WARN":
            return 0  # Warnings don't fail the build
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
