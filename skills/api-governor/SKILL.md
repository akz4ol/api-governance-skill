---
name: API Governor
description: Lints OpenAPI specs against an opinionated but configurable API governance policy, detects breaking changes vs a baseline spec, and generates merge-ready governance artifacts (review, changelog, deprecation plan).
---

# API Governor Skill

## Scope
Use this skill when you need consistent, actionable governance for HTTP APIs described in OpenAPI (YAML/JSON), including:
- Design linting (resource modeling, naming, pagination, errors)
- Security governance (auth requirements, scopes/roles, sensitive fields notes)
- Reliability governance (idempotency guidance, retry semantics)
- Observability governance (request IDs/correlation headers)
- Breaking-change detection (new spec vs baseline spec) + deprecation plan

This skill is optimized for **internal APIs by default** (pragmatic policy). A strict public-API preset is also provided.

## Inputs expected
Provide at least one OpenAPI spec file (preferred):
- `openapi.yaml`, `openapi.yml`, `openapi.json`, `swagger.yaml`, etc.

Optional but strongly recommended for breaking-change checks:
- A baseline spec (e.g., from `main`) to compare against.

Optional policy override:
- A policy YAML file (default policy is `policy/default.internal.yaml`).

## Outputs produced (stable contract)
Write outputs to `governance/` (or the user-specified output directory):

1) `API_REVIEW.md` (always)
- Summary (PASS/WARN/FAIL)
- Findings by severity (BLOCKER/MAJOR/MINOR/INFO)
- Recommended fixes with examples
- Checklist results

2) `API_CHANGELOG.md` (only in diff mode)
- Non-breaking changes
- Breaking changes (with client impact)
- Deprecations introduced

3) `DEPRECATION_PLAN.md` (only if breaking changes exist or policy requires it)
- Timeline and version strategy
- Client migration notes
- Communication template
- Sunset criteria

Optional outputs (if enabled):
- `SECURITY_NOTES.md`
- `OPENAPI_PATCHES/` (snippets or diffs)

## Procedure (how to execute the skill)
### Step 1 — Discover the API specs
- If a spec path is provided, use it.
- Else search the repo for common filenames: `openapi.*`, `swagger.*`, `*.openapi.*`.

### Step 2 — Validate spec integrity
- Parse YAML/JSON.
- Validate internal references (`$ref`) resolvable.
- Report structural OpenAPI violations as BLOCKER.

### Step 3 — Apply governance policy rules
Evaluate the spec against the selected policy:
- Resource modeling and naming conventions
- Consistent error envelope
- Pagination and filtering conventions
- Versioning conventions and deprecation markers
- Security requirements (auth schemes; scopes/roles)
- Reliability (idempotency headers for unsafe operations where applicable)
- Observability (correlation/request ID headers)

### Step 4 — Breaking-change analysis (if baseline provided)
Compare the current spec against the baseline:
- Removed endpoints/operations
- Removed/renamed parameters
- Response schema contract changes (removed fields; tightened constraints)
- Required/optional flips
- Auth changes that impact clients
- Status code behavioral changes
Classify changes as BREAKING or NON-BREAKING, then escalate severity per policy.

### Step 5 — Generate governance artifacts
Write:
- `API_REVIEW.md` (always)
- `API_CHANGELOG.md` (diff mode)
- `DEPRECATION_PLAN.md` (when breaking changes or required by strict preset)

### Step 6 — Suggest minimal, safe remediations
For each BLOCKER/MAJOR finding:
- Provide a concrete remediation path
- Prefer incremental and backward-compatible steps
- If breaking change unavoidable, provide deprecation/migration plan

## Quality gates (must satisfy)
- Every operation MUST declare or inherit security (unless explicitly marked public by policy).
- Error responses MUST use the standard error model (policy-defined).
- If pagination is used, it MUST follow the policy's chosen convention.
- Any breaking change MUST either:
  - be blocked (internal default may allow with plan), or
  - include deprecation + migration plan (strict preset requires this).

## Severity semantics
- **BLOCKER**: Should not merge. Usually breaks clients or violates core governance (invalid spec, missing auth in strict areas, breaking changes without plan under strict preset).
- **MAJOR**: Merge discouraged until fixed; meaningful client/developer pain (inconsistent error model, undocumented pagination).
- **MINOR**: Style and consistency improvements (tag hygiene, operationId conventions).
- **INFO**: Suggestions and best practices (examples, descriptions).

## Failure modes & recovery
- If spec is missing: produce `API_REVIEW.md` explaining how to provide spec paths.
- If parsing fails: provide file+line parse error guidance (BLOCKER).
- If policy conflicts with current API style: suggest an incremental adoption plan.

## Templates and examples
See:
- `resources/examples/` for demo specs and expected outputs.
- `resources/standards/` for governance rationale and conventions.
- `policy/` for default internal policy and strict preset.

## Tooling hooks (optional)
If your environment supports running scripts:
- `scripts/api_governance.py --spec <path> --policy <path> --baseline <path> --out <dir>`
- `scripts/diff_openapi.py` for breaking change detection only
- `scripts/lint_openapi.py` for schema checks only
