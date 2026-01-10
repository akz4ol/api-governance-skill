# Policies

## Built-in Policies

### Pragmatic Internal (Default)

For internal APIs with reasonable governance:

```bash
api-governor openapi.yaml
```

Key settings:
- Security missing → MAJOR
- Error model issues → MAJOR
- Breaking changes → MAJOR (BLOCKER if no deprecation plan)
- Naming issues → MINOR

### Strict Public

For public APIs with strict governance:

```bash
api-governor openapi.yaml --strict
```

Key settings:
- Security missing → BLOCKER
- Error model issues → BLOCKER
- Breaking changes → BLOCKER
- operationId required
- Tags required
- OAuth2 only

## Custom Policies

Create a YAML file:

```yaml
policy_name: "My Custom Policy"
policy_version: "1.0"

enforcement:
  default_severity:
    security_missing: "BLOCKER"
    error_model_inconsistent: "MAJOR"

security:
  require_security_by_default: true
  auth_schemes_allowed:
    - "bearerAuth"
    - "oauth2"

pagination:
  style: "cursor"
  required_for_list_endpoints: true

breaking_change_detection:
  enabled: true
  default_breaking_severity: "BLOCKER"
```

Use it:

```bash
api-governor openapi.yaml --policy my-policy.yaml
```

## Policy Schema

See the [full schema reference](../reference/policy-schema.md).
