# API Changelog (Spec Diff)

## Breaking Changes
- `GET /users` response changed from object `{items, nextCursor}` to `{data}`.
- `GET /users` query params changed: removed `cursor`, renamed `limit` to `pageSize`.
- `User.email` removed from schema.

## Non-breaking Changes
- None detected.

## Deprecations Introduced
- None declared (consider adding `deprecated: true` markers per policy).
