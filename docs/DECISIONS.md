# Architectural Decision Records

This document captures key architectural decisions made in api-governance-skill.

---

## ADR-001: Policy-Driven Configuration Over Hardcoded Rules

**Date**: 2024-01

### Context

We need to support different governance standards for different API types (internal vs. public, startup vs. enterprise).

### Options Considered

1. **Hardcoded rules** — Simple but inflexible
2. **Configuration files** — Flexible but requires learning curve
3. **Plugin system** — Maximum flexibility but high complexity

### Decision

Use YAML-based policy files with sensible defaults.

### Consequences

- **Positive**: Users can customize without code changes
- **Positive**: Presets enable quick adoption (internal, strict)
- **Negative**: Policy schema is another thing to learn
- **Mitigated by**: Good defaults and comprehensive examples

---

## ADR-002: Severity Levels (BLOCKER/MAJOR/MINOR/INFO)

**Date**: 2024-01

### Context

Not all findings are equal. Some should block merges, others are suggestions.

### Options Considered

1. **Binary (pass/fail)** — Simple but too coarse
2. **3-level (error/warning/info)** — Standard but doesn't distinguish blocking
3. **4-level (blocker/major/minor/info)** — Explicit blocking semantics

### Decision

Use 4-level severity with BLOCKER explicitly meaning "do not merge."

### Consequences

- **Positive**: Clear guidance on what to fix now vs. later
- **Positive**: CI can key on blocker count for exit code
- **Negative**: Slight learning curve for severity levels
- **Mitigated by**: Clear documentation and consistent defaults

---

## ADR-003: Generate Markdown Artifacts (Not Just Findings)

**Date**: 2024-01

### Context

Raw findings are useful for machines but hard to review. API reviews need human-readable context.

### Options Considered

1. **JSON only** — Machine-readable, not review-friendly
2. **Markdown files** — Human-readable, commit-able
3. **HTML reports** — Rich but requires viewer

### Decision

Generate markdown artifacts: API_REVIEW.md, API_CHANGELOG.md, DEPRECATION_PLAN.md.

### Consequences

- **Positive**: Files can be committed to PRs and reviewed inline
- **Positive**: Changelogs serve as API documentation
- **Negative**: Need to keep artifact format consistent
- **Mitigated by**: Structured templates, not free-form text

---

## ADR-004: Breaking Change Detection via Spec Diff

**Date**: 2024-01

### Context

Breaking changes cause production incidents. Need automated detection.

### Options Considered

1. **Schema-level diff** — Misses semantic changes
2. **Operation-level diff** — Catches most breaking changes
3. **Deep semantic diff** — Catches everything but complex to implement

### Decision

Operation-level diff that detects: removed operations, required param changes, response schema narrowing, enum narrowing, auth changes.

### Consequences

- **Positive**: Catches 90% of breaking changes with reasonable complexity
- **Positive**: Clear categorization of breaking vs. non-breaking
- **Negative**: May miss subtle semantic changes
- **Mitigated by**: DEPRECATION_PLAN.md prompts human review

---

## ADR-005: No Runtime Dependencies Beyond PyYAML

**Date**: 2024-01

### Context

Library should be easy to install and have minimal attack surface.

### Options Considered

1. **Use full OpenAPI parser (e.g., openapi-core)** — Feature-rich but heavy
2. **Custom YAML parsing** — Lightweight but needs ref resolution
3. **Hybrid** — YAML + minimal ref resolution

### Decision

Use PyYAML with custom $ref resolution. Avoid heavy OpenAPI validation libraries.

### Consequences

- **Positive**: Fast installation, small footprint
- **Positive**: No version conflicts with user's OpenAPI tooling
- **Negative**: Need to implement ref resolution
- **Mitigated by**: Focused ref resolution (don't need full dereferencing)

---

## ADR-006: Rule IDs with Category Prefix

**Date**: 2024-01

### Context

Findings need stable, searchable identifiers.

### Options Considered

1. **Numeric only** — Simple but no grouping
2. **Category prefix (SEC001)** — Grouped and memorable
3. **UUID** — Unique but not human-friendly

### Decision

Use category prefix format: SEC001, ERR001, PAG001, NAM001, OBS001, VER001, BREAK001.

### Consequences

- **Positive**: Easy to search and filter by category
- **Positive**: Easy to discuss ("we have a SEC001 violation")
- **Negative**: Need to maintain category namespaces
- **Mitigated by**: Clear category definitions in documentation

---

## ADR-007: Exit Code Semantics

**Date**: 2024-01

### Context

CI/CD pipelines need clear signals for pass/fail.

### Decision

- Exit 0: No blockers (pass)
- Exit 1: One or more blockers (fail)

### Consequences

- **Positive**: Simple integration with any CI system
- **Positive**: MAJOR/MINOR don't block by default (configurable)
- **Note**: Users can configure MAJOR → BLOCKER escalation in policy

---

## Future Decisions to Make

- [ ] Plugin system for custom rules
- [ ] AsyncAPI support
- [ ] Multi-file workspace support
- [ ] SARIF output format
