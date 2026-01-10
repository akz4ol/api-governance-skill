# API Governor - API Documentation

## Python API

### Quick Start

```python
from api_governor import APIGovernor

# Basic usage
governor = APIGovernor(
    spec_path="openapi.yaml",
    baseline_path="openapi-baseline.yaml",  # optional
)

# Run analysis
result = governor.run()
print(f"Status: {result.status}")
print(f"Blockers: {len(result.blockers)}")

# Generate artifacts
artifacts = governor.generate_artifacts()
for name, path in artifacts.items():
    print(f"Generated: {path}")
```

### APIGovernor Class

```python
class APIGovernor:
    def __init__(
        self,
        spec_path: str | Path,
        policy_path: str | Path | None = None,
        baseline_path: str | Path | None = None,
        output_dir: str | Path = "governance",
    ):
        """
        Initialize API Governor.

        Args:
            spec_path: Path to OpenAPI spec file to analyze
            policy_path: Path to policy YAML (default: pragmatic internal)
            baseline_path: Path to baseline spec for breaking change detection
            output_dir: Directory for output artifacts
        """

    def run(self) -> GovernanceResult:
        """
        Run governance analysis.

        Returns:
            GovernanceResult with findings, breaking changes, and checklist
        """

    def generate_artifacts(self, result: GovernanceResult | None = None) -> dict[str, Path]:
        """
        Generate output artifacts.

        Args:
            result: Previous result (runs analysis if not provided)

        Returns:
            Dict mapping artifact names to file paths
        """
```

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

    @property
    def blockers(self) -> list[Finding]: ...
    @property
    def majors(self) -> list[Finding]: ...
    @property
    def minors(self) -> list[Finding]: ...
    @property
    def infos(self) -> list[Finding]: ...
```

### Finding

```python
@dataclass
class Finding:
    rule_id: str           # e.g., "SEC001"
    severity: Severity     # BLOCKER, MAJOR, MINOR, INFO
    message: str           # Human-readable description
    path: str | None       # JSON path in spec
    line: int | None       # Line number if available
    recommendation: str | None  # How to fix
```

### BreakingChange

```python
@dataclass
class BreakingChange:
    change_type: str       # e.g., "removed_operation"
    path: str              # Affected path
    description: str       # What changed
    client_impact: str     # How it affects clients
    severity: Severity
```

## CLI Reference

```bash
# Basic usage
api-governor openapi.yaml

# With baseline for breaking change detection
api-governor openapi.yaml --baseline openapi-v1.yaml

# Use strict public API policy
api-governor openapi.yaml --strict

# Custom policy
api-governor openapi.yaml --policy my-policy.yaml

# Output as JSON
api-governor openapi.yaml --json

# Custom output directory
api-governor openapi.yaml --output ./governance-reports
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PASS or WARN |
| 1 | FAIL (blockers found) |
| 2 | File not found |
| 3 | Other error |

## Rule IDs

### Security (SEC)
- `SEC001`: Missing security requirement on operation

### Errors (ERR)
- `ERR001`: Missing standard error schema
- `ERR002`: Error schema missing required field

### Pagination (PAG)
- `PAG001`: Missing limit parameter on list endpoint
- `PAG002`: Missing cursor parameter for cursor pagination

### Naming (NAM)
- `NAM001`: Path segment not in kebab-case
- `NAM002`: Verb in path segment

### Observability (OBS)
- `OBS001`: Error schema missing requestId field

### Versioning (VER)
- `VER001`: URL versioning required but not found

### Breaking Changes (BREAK)
- `BREAK001`: Breaking changes detected without deprecation plan

### Parsing (PARSE, REF)
- `PARSE001`: Failed to parse OpenAPI spec
- `REF001`: Unresolved $ref reference

## Policy Configuration

See `policy/default.internal.yaml` for the full policy structure.

### Key Policy Sections

```yaml
enforcement:
  default_severity:
    security_missing: "MAJOR"  # Override severity per rule type

api_style:
  prefer_kebab_case_paths: true
  discourage_verbs_in_paths: true

pagination:
  style: "cursor"  # cursor, offset, or page
  required_for_list_endpoints: true

security:
  require_security_by_default: true
  auth_schemes_allowed: ["bearerAuth", "oauth2"]

breaking_change_detection:
  enabled: true
  default_breaking_severity: "MAJOR"
  escalate_to_blocker_if:
    no_deprecation_plan: true
```
