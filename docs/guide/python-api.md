# Python API

## APIGovernor Class

```python
from api_governor import APIGovernor

governor = APIGovernor(
    spec_path="openapi.yaml",
    policy_path="policy.yaml",      # optional
    baseline_path="baseline.yaml",  # optional
    output_dir="governance",        # optional
)
```

### Methods

#### `run() -> GovernanceResult`

Run governance analysis.

```python
result = governor.run()
print(result.status)      # "PASS", "WARN", or "FAIL"
print(result.blockers)    # List of BLOCKER findings
print(result.majors)      # List of MAJOR findings
```

#### `generate_artifacts(result=None) -> dict[str, Path]`

Generate output artifacts.

```python
artifacts = governor.generate_artifacts()
# {'API_REVIEW.md': Path('governance/API_REVIEW.md'), ...}
```

## Data Models

### GovernanceResult

```python
@dataclass
class GovernanceResult:
    spec_path: str
    policy_name: str
    status: str  # "PASS", "WARN", "FAIL"
    findings: list[Finding]
    breaking_changes: list[BreakingChange]
    checklist: dict[str, bool]
```

### Finding

```python
@dataclass
class Finding:
    rule_id: str           # e.g., "SEC001"
    severity: Severity     # BLOCKER, MAJOR, MINOR, INFO
    message: str
    path: str | None       # JSON path in spec
    recommendation: str | None
```

### BreakingChange

```python
@dataclass
class BreakingChange:
    change_type: str       # e.g., "removed_operation"
    path: str
    description: str
    client_impact: str
    severity: Severity
```
