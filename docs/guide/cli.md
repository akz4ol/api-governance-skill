# CLI Reference

## Synopsis

```bash
api-governor [OPTIONS] SPEC
```

## Arguments

| Argument | Description |
|----------|-------------|
| `SPEC` | Path to OpenAPI spec file (required) |

## Options

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `--policy PATH` | Path to policy YAML file |
| `--baseline PATH` | Baseline spec for breaking change detection |
| `-o, --output PATH` | Output directory (default: `governance/`) |
| `--json` | Output as JSON instead of artifacts |
| `--strict` | Use strict public API policy |

## Examples

### Basic Check
```bash
api-governor openapi.yaml
```

### Breaking Change Detection
```bash
api-governor openapi.yaml --baseline openapi-v1.yaml
```

### JSON Output
```bash
api-governor openapi.yaml --json | jq '.findings'
```

### Custom Output Directory
```bash
api-governor openapi.yaml -o ./reports
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PASS or WARN |
| 1 | FAIL (blockers found) |
| 2 | File not found |
| 3 | Other error |
