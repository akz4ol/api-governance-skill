# API Governor

**API governance and breaking change detection for OpenAPI specs**

API Governor helps you enforce consistent API design standards across your organization by linting OpenAPI specifications against configurable policies.

## Features

- **Design Governance** - Resource naming, pagination, error envelopes
- **Security Governance** - Auth requirements, scopes, sensitive fields
- **Reliability Governance** - Idempotency headers, retry semantics
- **Breaking Change Detection** - Compare specs and identify breaking changes
- **Artifact Generation** - Review reports, changelogs, deprecation plans

## Quick Install

```bash
pip install api-governor
```

## Quick Usage

```bash
# Basic governance check
api-governor openapi.yaml

# With breaking change detection
api-governor openapi.yaml --baseline openapi-v1.yaml

# Use strict public API policy
api-governor openapi.yaml --strict
```

## Output Artifacts

```
governance/
├── API_REVIEW.md      # Findings by severity
├── API_CHANGELOG.md   # Breaking vs non-breaking changes
└── DEPRECATION_PLAN.md # Migration guidance
```

## Next Steps

- [Installation](getting-started/installation.md)
- [Quick Start Guide](getting-started/quickstart.md)
- [CLI Reference](guide/cli.md)
- [Policy Configuration](guide/policies.md)
