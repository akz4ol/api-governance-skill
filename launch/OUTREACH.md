# Cross-Repo Outreach Strategy

Adjacent repos to integrate with or link from.

---

## High Priority (Direct Overlap)

### 1. Spectral (stoplightio/spectral)
**Stars**: 4.5k+ | **Relationship**: Complementary

**Action**: Open issue proposing integration
```
Title: Integration with api-governance-skill for artifact generation

Spectral is great for custom linting rules.
api-governance-skill adds breaking change detection and artifact generation.

Potential integration:
- Use Spectral for rule evaluation
- Use api-governance-skill for artifacts (REVIEW.md, CHANGELOG.md)

Would maintainers be interested in exploring this?
```

### 2. openapi-diff (OpenAPITools/openapi-diff)
**Stars**: 800+ | **Relationship**: Overlapping (breaking changes)

**Action**: Add to "Related Projects" in their README
```
PR Title: docs: Add api-governance-skill to related projects

api-governance-skill provides breaking change detection plus:
- Governance linting
- Artifact generation (deprecation plans)
```

### 3. Optic (opticdev/optic)
**Stars**: 1.5k+ | **Relationship**: Adjacent

**Action**: Open discussion
```
Title: Comparison: Optic vs api-governance-skill

For users evaluating options:
- Optic: CI-first API design, traffic verification
- api-governance-skill: Policy-driven linting + artifacts

Could we link to each other as alternatives?
```

---

## Medium Priority (Ecosystem)

### 4. FastAPI (tiangolo/fastapi)
**Stars**: 70k+ | **Relationship**: User overlap

**Action**: Add to awesome-fastapi list (if exists) or community discussions
```
Title: Governance tool for FastAPI OpenAPI specs

For FastAPI users generating OpenAPI specs:
api-governance-skill can lint and validate your generated specs.

Example workflow:
1. FastAPI generates openapi.json
2. api-governance-skill validates governance rules
3. CI blocks if issues found
```

### 5. drf-spectacular (tfranzel/drf-spectacular)
**Stars**: 2k+ | **Relationship**: User overlap

**Action**: Mention in discussions
```
For Django REST Framework users with drf-spectacular:
You can validate generated OpenAPI specs with api-governance-skill.
```

### 6. redocly-cli (Redocly/redocly-cli)
**Stars**: 900+ | **Relationship**: Complementary

**Action**: Open discussion about complementary workflows
```
Redocly for documentation generation
api-governance-skill for governance validation

Complementary workflow for API teams.
```

---

## Lower Priority (Broader Ecosystem)

### 7. openapi-generator (OpenAPITools/openapi-generator)
**Stars**: 20k+ | **Relationship**: Adjacent

**Action**: Community discussion
```
Before generating client/server code, validate specs with governance checks.
```

### 8. swagger-editor (swagger-api/swagger-editor)
**Stars**: 8k+ | **Relationship**: User overlap

**Action**: Community mention
```
Complement Swagger Editor with automated governance in CI.
```

### 9. prism (stoplightio/prism)
**Stars**: 4k+ | **Relationship**: User overlap

**Action**: Cross-mention in community
```
Validate specs before mocking with Prism.
```

### 10. bump-sh (bump-sh/cli)
**Stars**: 200+ | **Relationship**: Adjacent (docs)

**Action**: Propose integration for changelog generation
```
Combine api-governance-skill changelogs with Bump.sh documentation.
```

---

## Outreach Templates

### PR Template: Add to Related Projects

```markdown
## Description
Add api-governance-skill to the list of related projects.

api-governance-skill provides:
- Policy-driven OpenAPI linting
- Breaking change detection
- Artifact generation (API_REVIEW.md, CHANGELOG.md, DEPRECATION_PLAN.md)

## Why Related
[Explain how it complements this project]

## Links
- GitHub: https://github.com/akz4ol/api-governance-skill
- Docs: https://akz4ol.github.io/api-governance-skill
```

### Issue Template: Propose Integration

```markdown
## Summary
Exploring integration between [this project] and api-governance-skill.

## What api-governance-skill Does
- Policy-driven OpenAPI spec governance
- Breaking change detection between spec versions
- Artifact generation (review reports, changelogs, deprecation plans)

## Potential Integration
[Specific integration idea]

## Questions for Maintainers
1. Is this something you'd consider supporting?
2. Any technical concerns?
3. Would a PR be welcome?
```

---

## Tracking

| Repo | Action | Status | Date | Response |
|------|--------|--------|------|----------|
| Spectral | Issue | TODO | | |
| openapi-diff | PR | TODO | | |
| Optic | Discussion | TODO | | |
| FastAPI | Community | TODO | | |
| drf-spectacular | Discussion | TODO | | |
| redocly-cli | Discussion | TODO | | |
