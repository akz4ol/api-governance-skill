# Frequently Asked Questions

## General

### What's the difference between this and Spectral?

Spectral is a general-purpose OpenAPI linter with customizable rules. api-governance-skill is focused on:

1. **Breaking change detection** — Compares spec versions
2. **Artifact generation** — Produces review reports, changelogs, deprecation plans
3. **Opinionated presets** — Ready-to-use policies for internal vs. public APIs

Use Spectral for custom linting rules. Use api-governance-skill for governance workflows with artifacts.

### Does this replace human API review?

No. It augments human review by:
- Catching common issues automatically
- Ensuring consistency across reviewers
- Generating documentation that would otherwise be manual

Humans still need to review business logic, naming choices, and edge cases.

### What OpenAPI versions are supported?

- OpenAPI 3.0.x — Full support
- OpenAPI 3.1.x — Partial support (JSON Schema dialect differences)
- OpenAPI 2.0 (Swagger) — Not supported

---

## Installation & Setup

### How do I install this?

```bash
pip install api-governor
```

Or from source:
```bash
git clone https://github.com/akz4ol/api-governance-skill.git
cd api-governance-skill
pip install -e .
```

### What Python versions are supported?

Python 3.10, 3.11, and 3.12.

### Can I use this in Docker?

Yes:
```bash
docker build -t api-governor .
docker run --rm -v $(pwd):/specs api-governor /specs/openapi.yaml
```

---

## Usage

### How do I check for breaking changes?

Provide a baseline spec:
```bash
api-governor current.yaml --baseline previous.yaml
```

### How do I use a strict policy?

```bash
api-governor openapi.yaml --strict
```

Or specify a policy file:
```bash
api-governor openapi.yaml --policy my-policy.yaml
```

### How do I integrate with CI/CD?

Check the exit code:
- Exit 0 = No blockers (pass)
- Exit 1 = One or more blockers (fail)

Example GitHub Actions:
```yaml
- name: API Governance Check
  run: api-governor openapi.yaml --strict
```

### How do I get JSON output instead of text?

```bash
api-governor openapi.yaml --json
```

### Where are the generated artifacts?

By default in `governance/`:
- `API_REVIEW.md` — Findings by severity
- `API_CHANGELOG.md` — Breaking vs. non-breaking changes
- `DEPRECATION_PLAN.md` — Migration guidance

Custom directory:
```bash
api-governor openapi.yaml --output ./api-docs
```

---

## Rules & Policies

### What rules are checked by default?

| Category | Rules |
|----------|-------|
| Security | Missing auth, weak schemes |
| Errors | Missing error schema |
| Pagination | Missing limit/cursor |
| Naming | Non-kebab paths, verbs in paths |
| Observability | Missing request ID |
| Breaking | Removed operations, param changes |

See [Rule Reference](reference/rules.md) for full list.

### How do I disable a specific rule?

In your policy file:
```yaml
rules:
  NAM001:
    enabled: false
```

### How do I change a rule's severity?

In your policy file:
```yaml
rules:
  SEC001:
    severity: BLOCKER  # was MAJOR
```

### What's the difference between internal and strict policies?

| Aspect | Internal | Strict |
|--------|----------|--------|
| Security missing | MAJOR | BLOCKER |
| Breaking changes | Allowed with plan | Never allowed |
| Naming violations | MINOR | MAJOR |

Internal is for move-fast teams. Strict is for public APIs.

---

## Troubleshooting

### "Failed to parse OpenAPI spec"

Check that your spec is valid YAML/JSON and conforms to OpenAPI 3.x schema. Use `openapi-spec-validator` to check syntax first.

### "Unresolved $ref reference"

The tool resolves `$ref` within the same file. External file refs and URL refs are not fully supported yet.

Workaround: Bundle your spec into a single file using `swagger-cli bundle`.

### "No findings but I expected some"

Check your policy. Rules may be disabled or set to INFO severity. Use `--verbose` to see which rules ran.

### Performance is slow on large specs

For specs with 500+ operations, consider:
- Splitting into smaller specs
- Running only specific rule categories
- Using `--no-artifacts` to skip generation

---

## Contributing

### How do I add a new rule?

1. Add check function in `src/api_governor/rules.py`
2. Register in the rules list
3. Add documentation in `docs/reference/rules.md`
4. Add tests

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

### How do I report a bug?

Open an issue at: https://github.com/akz4ol/api-governance-skill/issues

Include:
- api-governor version
- OpenAPI spec (or minimal reproduction)
- Expected vs. actual behavior
