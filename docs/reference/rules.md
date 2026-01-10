# Rule Reference

## Security Rules (SEC)

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| SEC001 | Missing security requirement on operation | MAJOR |

## Error Rules (ERR)

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| ERR001 | Missing standard error schema | MAJOR |
| ERR002 | Error schema missing required field | MAJOR |

## Pagination Rules (PAG)

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| PAG001 | Missing limit parameter on list endpoint | MAJOR |
| PAG002 | Missing cursor parameter for cursor pagination | MAJOR |

## Naming Rules (NAM)

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| NAM001 | Path segment not in kebab-case | MINOR |
| NAM002 | Verb in path segment | MINOR |

## Observability Rules (OBS)

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| OBS001 | Error schema missing requestId field | MINOR |

## Versioning Rules (VER)

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| VER001 | URL versioning required but not found | MINOR |

## Breaking Change Rules (BREAK)

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| BREAK001 | Breaking changes detected without deprecation plan | BLOCKER |

## Parse Rules (PARSE, REF)

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| PARSE001 | Failed to parse OpenAPI spec | BLOCKER |
| REF001 | Unresolved $ref reference | BLOCKER |
