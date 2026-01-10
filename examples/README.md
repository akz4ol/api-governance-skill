# API Governor Examples

This directory contains working examples demonstrating the API Governor.

## Quick Start

```bash
# From the repository root
cd examples
python run_example.py
```

## Files

- `sample_openapi.yaml` - Example OpenAPI 3.0 specification
- `run_example.py` - Script demonstrating all features
- `output/` - Generated artifacts (created after running)

## Generated Artifacts

After running the example, you'll find:

```
output/
├── API_REVIEW.md              # Governance report with findings
├── api-governor-report.json   # JSON format for tooling
└── api-governor-report.sarif  # SARIF format for code scanning
```

## Sample Output

```
API Governor - Example
============================================================

1. Running governance checks...
   - Status: PASS
   - Total findings: 2
   - Blockers: 0
   - Majors: 0
   - Minors: 2

   Findings:
   - [MINOR] Operation GET /users/{userId} missing example in response

2. Writing markdown artifacts...
   - API_REVIEW.md: output/API_REVIEW.md

3. Generating JSON report...
   - output/api-governor-report.json

4. Generating SARIF report...
   - output/api-governor-report.sarif

5. Running custom rule plugins...
   - Registered plugins: 3
     - CUSTOM_REQUIRE_DESCRIPTION: Require Operation Description
     - CUSTOM_REQUIRE_EXAMPLES: Require Schema Examples
     - CUSTOM_MAX_PATH_DEPTH: Maximum Path Depth
   - Plugin findings: 1

6. Governance checklist:
   [✓] All endpoints have security defined
   [✓] Pagination parameters use standard names
   [✓] Error responses follow standard format
```

## GitHub Actions Usage

```yaml
name: API Governance
on: [pull_request]

jobs:
  govern:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: API Governance Check
        uses: akz4ol/api-governance-skill@v1
        with:
          spec-path: openapi.yaml
          policy: strict
          fail-on: blocker
```

## Custom Plugins

Create your own governance rules:

```python
from api_governor import RulePlugin, Finding, Severity

class NoDeleteRule(RulePlugin):
    @property
    def rule_id(self):
        return "NO_DELETE"

    @property
    def name(self):
        return "No DELETE Operations"

    @property
    def description(self):
        return "Prevent DELETE operations in API"

    def check(self, spec, policy):
        findings = []
        for path, method, op in spec.get_operations():
            if method == "delete":
                findings.append(Finding(
                    rule_id=self.rule_id,
                    severity=Severity.BLOCKER,
                    message=f"DELETE not allowed: {path}",
                    path=path,
                ))
        return findings
```
