# API Governance Skill

[![CI](https://github.com/akz4ol/api-governance-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/akz4ol/api-governance-skill/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**A library that validates OpenAPI specs against configurable governance policies, enabling consistent, secure, well-documented APIs.**

---

## Why This Exists

- **API reviews are inconsistent** — Different reviewers catch different issues, leading to style drift across services
- **Breaking changes slip through** — Without automated detection, backward-incompatible changes break consumers
- **Security gaps go unnoticed** — Missing auth, weak schemes, and exposed sensitive fields aren't caught until production
- **Documentation is manual** — Writing API changelogs and deprecation plans is tedious and often skipped

## What It Is

- A **policy-driven linter** for OpenAPI 3.0/3.1 specs
- A **breaking change detector** that compares spec versions
- An **artifact generator** that produces review reports, changelogs, and deprecation plans
- **Configurable** — from pragmatic internal APIs to strict public API standards

## What It Is NOT

- Not a spec validator (use `openapi-spec-validator` for syntax)
- Not an API gateway or runtime enforcement
- Not a replacement for human review — it augments reviewers with automated checks

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                     API Governance Pipeline                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐  │
│  │ OpenAPI  │───▶│  Parser  │───▶│  Rules   │───▶│   Findings   │  │
│  │   Spec   │    │          │    │  Engine  │    │ (by severity)│  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────┘  │
│                                         │                           │
│                        ┌────────────────┘                           │
│                        ▼                                            │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────────────┐  │
│  │ Baseline │───▶│  Differ  │───▶│     Breaking Changes         │  │
│  │   Spec   │    │          │    │  (removed/changed/narrowed)  │  │
│  └──────────┘    └──────────┘    └──────────────────────────────┘  │
│                                         │                           │
│                        ┌────────────────┘                           │
│                        ▼                                            │
│               ┌─────────────────────────────────────────────────┐   │
│               │              Output Artifacts                    │   │
│               │  • API_REVIEW.md    (findings by severity)      │   │
│               │  • API_CHANGELOG.md (breaking + non-breaking)   │   │
│               │  • DEPRECATION_PLAN.md (migration guidance)     │   │
│               └─────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 30-Second Hello World

```bash
pip install api-governor

# Check a spec against default policy
api-governor openapi.yaml
```

### 2-Minute Realistic Example

```bash
# Compare versions and detect breaking changes
api-governor openapi-v2.yaml --baseline openapi-v1.yaml --strict

# Output:
# BLOCKER: BREAK001 - Breaking changes detected without deprecation plan
#   • Removed endpoint: DELETE /users/{id}
#   • Required parameter added: GET /users now requires 'tenant_id'
#
# MAJOR: SEC001 - Missing security on POST /orders
# MINOR: NAM001 - Path '/getUsers' contains verb
```

### Python API

```python
from api_governor import APIGovernor

governor = APIGovernor(
    spec_path="openapi.yaml",
    baseline_path="openapi-v1.yaml",  # optional
)

result = governor.run()
print(f"Status: {result.status}")  # PASS, WARN, or FAIL
print(f"Blockers: {len(result.blockers)}")

# Generate artifacts
artifacts = governor.generate_artifacts()
# Creates: governance/API_REVIEW.md, API_CHANGELOG.md, DEPRECATION_PLAN.md
```

### Docker

```bash
docker build -t api-governor .
docker run --rm -v $(pwd):/specs api-governor /specs/openapi.yaml
```

---

## Real-World Use Cases

| Use Case | Command | Outcome |
|----------|---------|---------|
| **PR gate** | `api-governor openapi.yaml --strict` | Block merges with security gaps |
| **Breaking change detection** | `api-governor v2.yaml --baseline v1.yaml` | Generate deprecation plans |
| **API consistency audit** | `api-governor *.yaml --policy corp-standard.yaml` | Enforce org-wide standards |
| **Documentation generation** | `api-governor openapi.yaml --artifacts` | Auto-generate changelogs |

---

## Comparison with Alternatives

| Tool | Focus | Breaking Changes | Artifacts | Configurable Policy |
|------|-------|------------------|-----------|---------------------|
| **api-governance-skill** | Governance + review | Yes | Yes | Yes |
| Spectral | Linting rules | No | No | Yes (custom rules) |
| openapi-diff | Diff only | Yes | No | No |
| Optic | API design | Yes | Limited | Limited |

**Key differentiator**: api-governance-skill produces merge-ready artifacts (review reports, changelogs, deprecation plans) — not just findings.

---

## Policies

| Policy | Use Case | Security | Breaking Changes |
|--------|----------|----------|------------------|
| `default.internal.yaml` | Internal APIs | MAJOR | Allowed with plan |
| `preset.strict.public.yaml` | Public APIs | BLOCKER | Never allowed |

### Custom Policy

```yaml
# my-policy.yaml
policy_name: my-company-api-standard
enforcement:
  default_severity:
    security_missing: BLOCKER
    naming_inconsistent: MINOR
security:
  require_security_by_default: true
  auth_schemes_allowed: [bearerAuth, oauth2]
```

```bash
api-governor openapi.yaml --policy my-policy.yaml
```

---

## Rule Categories

| Category | Rules | Default Severity |
|----------|-------|------------------|
| **SEC** (Security) | Missing auth, weak schemes | MAJOR |
| **ERR** (Errors) | Missing error schema, fields | MAJOR |
| **PAG** (Pagination) | Missing limit/cursor | MAJOR |
| **NAM** (Naming) | Non-kebab paths, verbs | MINOR |
| **OBS** (Observability) | Missing request ID | MINOR |
| **VER** (Versioning) | Missing URL version | MINOR |
| **BREAK** (Breaking) | Removed/changed operations | BLOCKER |

See [Rule Reference](docs/reference/rules.md) for full details.

---

## Output Artifacts

```
governance/
├── API_REVIEW.md      # Findings grouped by severity
├── API_CHANGELOG.md   # Breaking vs non-breaking changes
└── DEPRECATION_PLAN.md # Migration guidance (if breaking)
```

---

## Additional Features

### GitHub Actions Integration
Add to your workflow:

```yaml
- name: API Governance Check
  uses: akz4ol/api-governance-skill@v1
  with:
    spec-path: openapi.yaml
    baseline-spec: openapi-main.yaml  # Optional: for breaking change detection
    policy: strict
    fail-on: blocker
```

### JSON/SARIF Output
Generate machine-readable reports for tooling integration:

```python
from api_governor import JSONFormatter, SARIFFormatter

# JSON output
json_formatter = JSONFormatter(result)
json_formatter.write(output_dir)  # Creates api-governor-report.json

# SARIF output (for GitHub Code Scanning, VS Code, etc.)
sarif_formatter = SARIFFormatter(result)
sarif_formatter.write(output_dir)  # Creates api-governor-report.sarif
```

### Custom Rule Plugins
Extend with your own governance rules:

```python
from api_governor import RulePlugin, PluginManager, Finding, Severity

class MyCustomRule(RulePlugin):
    @property
    def rule_id(self):
        return "CUSTOM001"

    @property
    def name(self):
        return "My Custom Rule"

    @property
    def description(self):
        return "Enforces my custom standard"

    def check(self, spec, policy):
        findings = []
        # Your logic here
        return findings

# Register and use
manager = PluginManager()
manager.register(MyCustomRule)
findings = manager.run_all(spec, policy)
```

Built-in plugins: `RequireDescriptionRule`, `RequireExamplesRule`, `MaxPathDepthRule`

### VS Code Extension
Real-time API governance in your IDE:

```bash
cd vscode-extension
npm install && npm run compile
npm run package
code --install-extension api-governor-1.0.0.vsix
```

Features: Auto-lint on save, breaking change detection, full report generation.

---

## Roadmap

### Now ✅
- [x] OpenAPI 3.0/3.1 support
- [x] Core governance rules (security, naming, pagination)
- [x] Breaking change detection
- [x] Markdown artifact generation
- [x] GitHub Actions integration
- [x] JSON/SARIF output formats
- [x] Custom rule plugins
- [x] VS Code extension

### Next
- [ ] AsyncAPI support
- [ ] GraphQL schema governance
- [ ] Multi-spec workspace analysis

### Later
- [ ] API versioning strategy enforcement
- [ ] SDK generation validation

---

## Development

```bash
git clone https://github.com/akz4ol/api-governance-skill.git
cd api-governance-skill
pip install -e ".[dev]"

make test    # Run tests
make lint    # Run linters
make format  # Format code
make all     # All checks
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Good first issues:**
- Add new governance rule
- Improve error messages
- Add output format (JSON, SARIF)

---

## Documentation

- [Getting Started](docs/START_HERE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/reference/python-api.md)
- [Policy Schema](docs/reference/policy-schema.md)
- [Rule Reference](docs/reference/rules.md)
- [FAQ](docs/FAQ.md)
- [Architectural Decisions](docs/DECISIONS.md)

---

## License

MIT License - see [LICENSE](LICENSE) for details.
