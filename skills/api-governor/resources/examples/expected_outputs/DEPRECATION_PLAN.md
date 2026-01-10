# Deprecation & Migration Plan

## Overview
Breaking changes were introduced in API v2.0.0 affecting `GET /users` contract and `User` schema.

## Migration Strategy (Recommended)
**Option A (Preferred for internal pragmatic):**
- Reintroduce v1-compatible shapes:
  - Keep `limit` + `cursor`
  - Keep response `{ items, nextCursor }`
  - Keep `User.email` (nullable allowed)
- If new `data` shape is desired, add as **additional** field for 1 release cycle, then remove.

**Option B (Versioned endpoint):**
- Keep `/users` as v1 behavior.
- Add `/users/v2` (or a new tag/versioning approach) and publish migration instructions.

## Timeline
- Week 0: Announce deprecation and publish migration notes.
- Week 2: Provide compatibility layer or dual fields.
- Week 6: Sunset old behavior (only if all known clients migrated).

## Client Migration Notes
- Update client parsing to use `items` + `nextCursor` (policy standard).
- Do not rely on removal of `email` until sunset completed.

## Communication Template
Subject: Upcoming API change to GET /users
Body: We're introducing a revised response format; to avoid disruption, please migrate by <date>. Details: <link>.
