#!/usr/bin/env python3
"""Example usage of API Governor."""

from pathlib import Path

from api_governor import (
    APIGovernor,
    JSONFormatter,
    PluginManager,
    SARIFFormatter,
    default_manager,
)


def main() -> None:
    """Run the example."""
    # Paths
    example_dir = Path(__file__).parent
    spec_path = example_dir / "sample_openapi.yaml"
    output_dir = example_dir / "output"
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("API Governor - Example")
    print("=" * 60)

    # Initialize governor
    governor = APIGovernor(
        spec_path=spec_path,
        output_dir=output_dir,
    )

    # Run governance checks
    print("\n1. Running governance checks...")
    result = governor.run()

    print(f"   - Status: {result.status}")
    print(f"   - Total findings: {len(result.findings)}")
    print(f"   - Blockers: {len(result.blockers)}")
    print(f"   - Majors: {len(result.majors)}")
    print(f"   - Minors: {len(result.minors)}")

    # Show findings
    if result.findings:
        print("\n   Findings:")
        for finding in result.findings[:5]:  # Show first 5
            print(f"   - [{finding.severity.value}] {finding.message}")

    # Write markdown artifacts
    print("\n2. Writing markdown artifacts...")
    artifacts = governor.write_artifacts()
    for name, path in artifacts.items():
        print(f"   - {name}: {path}")

    # Generate JSON report
    print("\n3. Generating JSON report...")
    json_formatter = JSONFormatter(result)
    json_path = json_formatter.write(output_dir)
    print(f"   - {json_path}")

    # Generate SARIF report
    print("\n4. Generating SARIF report...")
    sarif_formatter = SARIFFormatter(result)
    sarif_path = sarif_formatter.write(output_dir)
    print(f"   - {sarif_path}")

    # Run custom plugins
    print("\n5. Running custom rule plugins...")
    print(f"   - Registered plugins: {len(default_manager.plugins)}")
    for plugin in default_manager.plugins:
        print(f"     - {plugin.rule_id}: {plugin.name}")

    plugin_findings = default_manager.run_all(governor._parser, governor._policy)
    print(f"   - Plugin findings: {len(plugin_findings)}")

    # Show checklist
    print("\n6. Governance checklist:")
    for item, passed in result.checklist.items():
        status = "✓" if passed else "✗"
        print(f"   [{status}] {item}")

    print("\n" + "=" * 60)
    print("Done! Check the 'output' directory for generated artifacts.")
    print("=" * 60)


if __name__ == "__main__":
    main()
