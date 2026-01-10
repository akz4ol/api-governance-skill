# Quick Start

## Basic Usage

Run governance check on an OpenAPI spec:

```bash
api-governor openapi.yaml
```

Output:
```
============================================================
API Governance Result: PASS
============================================================
Policy: Pragmatic Internal API Governance v1.0
Spec: openapi.yaml

Findings:
  BLOCKER: 0
  MAJOR:   0
  MINOR:   2
  INFO:    1

Generated Artifacts:
  API_REVIEW.md: governance/API_REVIEW.md
```

## Breaking Change Detection

Compare a new spec against a baseline:

```bash
api-governor openapi-v2.yaml --baseline openapi-v1.yaml
```

This generates:
- `API_REVIEW.md` - Governance findings
- `API_CHANGELOG.md` - List of changes
- `DEPRECATION_PLAN.md` - Migration guidance (if breaking changes found)

## Using Policies

### Default (Pragmatic Internal)
```bash
api-governor openapi.yaml
```

### Strict Public API
```bash
api-governor openapi.yaml --strict
```

### Custom Policy
```bash
api-governor openapi.yaml --policy my-policy.yaml
```

## Python API

```python
from api_governor import APIGovernor

governor = APIGovernor(
    spec_path="openapi.yaml",
    baseline_path="openapi-v1.yaml",
)

result = governor.run()
print(f"Status: {result.status}")
print(f"Blockers: {len(result.blockers)}")

# Generate artifacts
artifacts = governor.generate_artifacts()
```
