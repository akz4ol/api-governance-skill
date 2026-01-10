# Policy Schema Reference

## Top-Level Fields

```yaml
policy_name: string      # Required
policy_version: string   # Required
```

## Enforcement

```yaml
enforcement:
  default_severity:
    contract_validity: BLOCKER | MAJOR | MINOR | INFO
    security_missing: BLOCKER | MAJOR | MINOR | INFO
    error_model_inconsistent: BLOCKER | MAJOR | MINOR | INFO
    pagination_inconsistent: BLOCKER | MAJOR | MINOR | INFO
    versioning_inconsistent: BLOCKER | MAJOR | MINOR | INFO
    naming_inconsistent: BLOCKER | MAJOR | MINOR | INFO
    observability_missing: BLOCKER | MAJOR | MINOR | INFO
  allow_merge_with_breaking_changes_if:
    deprecation_plan_present: boolean
```

## API Style

```yaml
api_style:
  prefer_kebab_case_paths: boolean
  discourage_verbs_in_paths: boolean
  operation_id:
    required: boolean
    convention: camelCase | snake_case | kebab-case
  tags:
    required: boolean
```

## Security

```yaml
security:
  require_security_by_default: boolean
  allow_public_endpoints_if:
    explicitly_marked: boolean
    marker: string  # e.g., "x-public: true"
  require_scopes_if_oauth: boolean
  auth_schemes_allowed:
    - bearerAuth
    - apiKeyAuth
    - oauth2
```

## Pagination

```yaml
pagination:
  required_for_list_endpoints: boolean
  style: cursor | offset | page
  request_params:
    limit: string
    cursor: string
  response_shape:
    items: string
    nextCursor: string
  max_limit:
    enabled: boolean
    max: integer
```

## Breaking Change Detection

```yaml
breaking_change_detection:
  enabled: boolean
  default_breaking_severity: BLOCKER | MAJOR
  breaking_changes:
    removed_operation: boolean
    removed_parameter: boolean
    removed_response_field: boolean
    optional_to_required_flip: boolean
    narrowed_enum: boolean
    auth_requirement_change: boolean
  escalate_to_blocker_if:
    no_deprecation_plan: boolean
    any_breaking_change: boolean
```
