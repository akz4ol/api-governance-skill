# Architecture

This document describes the internal architecture of api-governance-skill.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          api-governance-skill                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────────────┐ │
│  │   CLI Layer    │───▶│   Governor     │───▶│   Output Generator    │ │
│  │  (__main__.py) │    │  (governor.py) │    │    (output.py)        │ │
│  └────────────────┘    └───────┬────────┘    └────────────────────────┘ │
│                                │                                         │
│                    ┌───────────┼───────────┐                            │
│                    ▼           ▼           ▼                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │
│  │     Parser     │  │  Rules Engine  │  │    Differ      │            │
│  │  (parser.py)   │  │   (rules.py)   │  │   (diff.py)    │            │
│  └────────────────┘  └────────────────┘  └────────────────┘            │
│                                │                                         │
│                                ▼                                         │
│                     ┌────────────────────┐                              │
│                     │   Data Models      │                              │
│                     │   (models.py)      │                              │
│                     └────────────────────┘                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Problem Statement

API governance is typically manual and inconsistent:
- Reviewers catch different issues based on experience
- Breaking changes aren't detected until consumers complain
- Security gaps require security team review bottleneck
- Documentation (changelogs, deprecation plans) is afterthought

## Non-Goals

- **Syntax validation**: Use `openapi-spec-validator` for that
- **Runtime enforcement**: We're a design-time linter
- **API gateway integration**: We produce reports, not gateway configs
- **Full semantic understanding**: We check patterns, not business logic

## Invariants

1. **Policy determines behavior**: All rules respect policy configuration
2. **Baseline is optional**: Tool works without breaking change detection
3. **Findings are actionable**: Every finding includes rule ID and location
4. **Exit codes are predictable**: 0 = no blockers, 1 = blockers exist

## Data Model

### Core Types

```python
@dataclass
class Finding:
    rule_id: str        # e.g., "SEC001"
    severity: Severity  # BLOCKER, MAJOR, MINOR, INFO
    message: str        # Human-readable description
    location: str       # e.g., "POST /orders"
    suggestion: str     # How to fix (optional)

@dataclass
class BreakingChange:
    change_type: str    # removed_operation, required_param_added, etc.
    path: str           # API path affected
    description: str    # What changed

@dataclass
class GovernanceResult:
    status: str         # PASS, WARN, FAIL
    findings: list[Finding]
    breaking_changes: list[BreakingChange]
    blockers: list[Finding]
    majors: list[Finding]
    minors: list[Finding]
```

## Key Algorithms

### 1. Policy Loading

```
policy = load_yaml(policy_file) ?? load_yaml(default_policy)
merge(policy, cli_overrides)
```

Policies cascade: defaults → preset → custom → CLI flags.

### 2. Rules Engine

```
for operation in spec.operations:
    for rule in enabled_rules:
        if rule.matches(operation):
            findings.append(rule.check(operation))
```

Rules are independent and can run in parallel (currently sequential for simplicity).

### 3. Breaking Change Detection

```
for path in baseline_spec.paths:
    if path not in current_spec.paths:
        breaking_changes.append(removed_operation)
    else:
        diff_operation(baseline_spec[path], current_spec[path])
```

Breaking change categories:
- Removed operation
- Required parameter added
- Optional-to-required flip
- Response field removed
- Enum values narrowed
- Auth requirement changed

### 4. Severity Escalation

```
if policy.escalate_to_blocker_if.any_breaking_change:
    for change in breaking_changes:
        change.severity = BLOCKER
```

Policy can escalate MAJOR → BLOCKER under specific conditions.

## Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `__main__.py` | CLI argument parsing, orchestration |
| `governor.py` | Main coordination, runs pipeline |
| `parser.py` | OpenAPI YAML parsing, $ref resolution |
| `rules.py` | Rule definitions, finding generation |
| `diff.py` | Spec comparison, breaking change detection |
| `models.py` | Data classes for findings, results |
| `output.py` | Markdown artifact generation |

## Extension Points

### Adding a New Rule

1. Add rule function to `rules.py`:
```python
def check_my_rule(operation: dict, policy: PolicyConfig) -> list[Finding]:
    findings = []
    if some_condition:
        findings.append(Finding(
            rule_id="MYR001",
            severity=Severity.MAJOR,
            message="Description of issue",
            location=operation["path"]
        ))
    return findings
```

2. Register in `RuleEngine.rules`:
```python
self.rules = [
    self.check_security,
    self.check_errors,
    self.check_my_rule,  # Add here
]
```

3. Add documentation to `docs/reference/rules.md`.

### Adding a New Output Format

1. Add formatter to `output.py`:
```python
def format_json(result: GovernanceResult) -> str:
    return json.dumps(asdict(result), indent=2)
```

2. Wire to CLI in `__main__.py`.

## Threat Model (Lightweight)

| Threat | Mitigation |
|--------|------------|
| Malicious spec crashes parser | YAML safe_load, exception handling |
| Policy injection | Policy is local file, not user input |
| Path traversal in $ref | Refs restricted to same directory |
| DoS via huge spec | Reasonable size limits (configurable) |

## Performance Assumptions

- **Spec size**: < 10MB, < 500 operations
- **Processing time**: < 5 seconds for typical spec
- **Memory**: < 500MB peak
- **Parallelism**: Not implemented (single-threaded)

For larger specs, consider spec splitting or async processing.

## Trade-offs and Failure Modes

### Trade-off: Simplicity vs. Completeness

We check common patterns, not every possible issue. A spec can pass governance checks and still have design problems.

**Mitigation**: Human review still required. Tool augments, doesn't replace.

### Trade-off: Policy Flexibility vs. Ease of Use

Highly configurable policies are powerful but complex.

**Mitigation**: Sensible presets (internal, strict). Most users never write custom policies.

### Trade-off: Markdown vs. Machine-Readable Output

Markdown artifacts are human-friendly but harder to integrate programmatically.

**Future**: Add JSON/SARIF output formats.

### Failure Mode: $ref Resolution

Complex $ref chains (refs to refs, external files) may fail.

**Current behavior**: Fail with clear error message.
**Future**: Better external ref support.

### Failure Mode: OpenAPI 3.1 Edge Cases

Full 3.1 support (JSON Schema dialect) is incomplete.

**Mitigation**: Document supported subset, add features incrementally.
