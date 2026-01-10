# API Review (API Governor)

## Summary
**Result:** FAIL
**Policy:** Pragmatic Internal API Governance v1.0
**Spec:** openapi_v2_breaking.yaml
**Baseline:** openapi_v1.yaml

## BLOCKER Findings
1) **Contract change breaks clients:** Response envelope for `GET /users` changed from `{ items, nextCursor }` to `{ data }`.
   - Impact: Clients expecting `items` and pagination cursors will fail or lose pagination support.
   - Recommended fix (preferred): Preserve `{ items, nextCursor }` and add `data` only as an alias (temporary) OR introduce `/users/v2` with deprecation plan.

## MAJOR Findings
1) **Breaking parameter rename:** `cursor/limit` pagination convention violated; `pageSize` introduced without `cursor`.
   - Recommended fix: Keep `limit` + `cursor` as primary. If you want page-size naming, add it as an optional alias while preserving `limit`.

2) **Breaking response schema change:** `User.email` field removed.
   - Recommended fix: Keep `email` (nullable if needed) for backward compatibility; mark deprecated if you plan to remove later.

## MINOR Findings
1) Missing `401` response definition on `GET /users` in v2.
   - Recommended fix: Add `401` with standard `Error` envelope.

## Checklist
- [x] OpenAPI parseable
- [x] Standard error envelope present
- [x] Security declared globally
- [ ] Pagination conforms to policy (limit+cursor; items+nextCursor)
- [ ] Breaking changes accompanied by deprecation plan (required by policy when breaking changes exist)

## Next Steps
- Create `governance/DEPRECATION_PLAN.md` describing:
  - Migration window
  - Client comms
  - Sunset criteria
- Amend OpenAPI to keep backward-compatible response and parameter shapes.
