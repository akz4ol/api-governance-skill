# Start Here

Welcome to api-governance-skill! This guide will get you from zero to productive in 5 minutes.

## What Is This?

api-governance-skill validates your OpenAPI specs against configurable governance policies, catches breaking changes before they ship, and generates review artifacts automatically.

**One-liner**: It's like ESLint for your API design, plus breaking change detection.

## Mental Model

```
Your OpenAPI Spec → [Rules Engine + Diff Engine] → Findings + Artifacts
```

1. **Parser** reads your OpenAPI spec
2. **Rules Engine** checks against policy (security, naming, pagination, errors)
3. **Differ** compares against baseline (if provided) for breaking changes
4. **Output Generator** produces markdown artifacts for review

## 3-Minute Quickstart

### Install

```bash
pip install api-governor
```

### Run Your First Check

```bash
# Download a sample spec
curl -O https://raw.githubusercontent.com/akz4ol/api-governance-skill/main/skills/api-governor/resources/examples/openapi_v1.yaml

# Run governance check
api-governor openapi_v1.yaml
```

### Detect Breaking Changes

```bash
# Download the breaking changes example
curl -O https://raw.githubusercontent.com/akz4ol/api-governance-skill/main/skills/api-governor/resources/examples/openapi_v2_breaking.yaml

# Compare versions
api-governor openapi_v2_breaking.yaml --baseline openapi_v1.yaml
```

## What You'll See

```
api-governor v1.0.0

Checking: openapi_v2_breaking.yaml
Baseline: openapi_v1.yaml
Policy: default.internal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BLOCKERS (1)
  BREAK001: Breaking changes without deprecation plan
    • Removed endpoint: DELETE /users/{id}

MAJOR (2)
  SEC001: Missing security on POST /orders
  ERR001: Missing error schema on GET /products

MINOR (1)
  NAM001: Path '/getUsers' contains verb

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Result: FAIL (1 blocker)
Artifacts written to: governance/
```

## Key Concepts

| Concept | What It Means |
|---------|---------------|
| **Policy** | Configuration that defines which rules apply and their severity |
| **Finding** | A violation detected by the rules engine |
| **Severity** | BLOCKER (stop), MAJOR (fix soon), MINOR (consider), INFO (FYI) |
| **Artifact** | Generated markdown file (review, changelog, deprecation plan) |

## Common Workflows

### 1. CI/CD Gate
```bash
# In your CI pipeline
api-governor openapi.yaml --strict
# Exit code: 0 = pass, 1 = blockers found
```

### 2. PR Review
```bash
# Compare PR branch spec to main branch spec
api-governor pr-branch/openapi.yaml --baseline main/openapi.yaml --artifacts
# Review governance/API_REVIEW.md
```

### 3. Custom Policy
```bash
api-governor openapi.yaml --policy my-company-policy.yaml
```

## Your First PR Idea

Here are some ways to contribute:

1. **Add a rule**: Look at `src/api_governor/rules.py` and add a new check
2. **Improve messages**: Make error messages clearer in `src/api_governor/output.py`
3. **Add output format**: Support JSON or SARIF output

See [CONTRIBUTING.md](../CONTRIBUTING.md) for setup instructions.

## Next Steps

- [Architecture](ARCHITECTURE.md) — How the internals work
- [Policy Schema](reference/policy-schema.md) — All configuration options
- [Rule Reference](reference/rules.md) — Every rule explained
- [FAQ](FAQ.md) — Common questions answered
