# API Governance Skill

[![CI](https://github.com/akz4ol/api-governance-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/akz4ol/api-governance-skill/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Lints OpenAPI specs against configurable governance policies, detects breaking changes, and generates merge-ready artifacts.

## Features

- **Design Governance**: Resource naming, pagination, error envelopes
- **Security Governance**: Auth requirements, scopes (OAuth), sensitive fields
- **Reliability Governance**: Idempotency headers, retry semantics
- **Observability Governance**: Request ID / correlation headers
- **Breaking Change Detection**: Removed endpoints, renamed params, schema changes
- **Artifact Generation**: Review reports, changelogs, deprecation plans

## Installation

```bash
# From PyPI
pip install api-governor

# From source
git clone https://github.com/akz4ol/api-governance-skill.git
cd api-governance-skill
pip install -e ".[dev]"
```

## Quick Start

### CLI Usage

```bash
# Basic governance check
api-governor openapi.yaml

# With breaking change detection
api-governor openapi.yaml --baseline openapi-v1.yaml

# Use strict public API policy
api-governor openapi.yaml --strict

# Output as JSON
api-governor openapi.yaml --json
```

### Python API

```python
from api_governor import APIGovernor

governor = APIGovernor(
    spec_path="openapi.yaml",
    baseline_path="openapi-v1.yaml",  # optional
)

result = governor.run()
print(f"Status: {result.status}")
print(f"Blockers: {len(result.blockers)}")

# Generate artifacts
artifacts = governor.generate_artifacts()
```

### Docker

```bash
# Build image
docker build -t api-governor .

# Run governance check
docker run --rm -v $(pwd):/specs api-governor /specs/openapi.yaml
```

## Output Artifacts

```
governance/
├── API_REVIEW.md      # Findings (BLOCKER/MAJOR/MINOR/INFO)
├── API_CHANGELOG.md   # Breaking vs non-breaking changes
└── DEPRECATION_PLAN.md # Migration guidance (if breaking changes)
```

## Policies

| Policy | Use Case |
|--------|----------|
| `default.internal.yaml` | Pragmatic internal APIs (default) |
| `preset.strict.public.yaml` | Public APIs with stricter requirements |

### Custom Policy

```bash
api-governor openapi.yaml --policy my-policy.yaml
```

See `skills/api-governor/policy/` for policy examples.

## Severity Levels

| Severity | Meaning | Action |
|----------|---------|--------|
| **BLOCKER** | Critical issue | Do not merge |
| **MAJOR** | Significant issue | Fix before merge |
| **MINOR** | Style/consistency | Consider fixing |
| **INFO** | Best practice | Optional improvement |

## Rule Categories

- **SEC**: Security rules (missing auth, weak schemes)
- **ERR**: Error handling rules (envelope, fields)
- **PAG**: Pagination rules (limit, cursor)
- **NAM**: Naming rules (kebab-case, no verbs)
- **OBS**: Observability rules (request ID)
- **VER**: Versioning rules (URL prefix)
- **BREAK**: Breaking change rules

## Directory Structure

```
api-governance-skill/
├── src/api_governor/       # Python package
├── skills/api-governor/    # Skill definition
│   ├── SKILL.md           # Skill documentation
│   ├── policy/            # Policy presets
│   └── resources/         # Examples
├── tests/                  # Test suite
├── schemas/               # JSON schemas
├── docs/                  # Documentation
├── Dockerfile             # Container support
└── Makefile              # Common tasks
```

## Development

```bash
# Install dev dependencies
make dev

# Run tests
make test

# Run linters
make lint

# Format code
make format

# Run all checks
make all
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Documentation

- [API Documentation](docs/API.md)
- [Skill Definition](skills/api-governor/SKILL.md)
- [Changelog](CHANGELOG.md)
