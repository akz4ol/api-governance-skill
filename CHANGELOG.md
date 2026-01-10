# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation

## [1.0.0] - 2025-01-10

### Added
- Core API governance skill with SKILL.md definition
- Pragmatic internal policy (`default.internal.yaml`)
  - Bearer/API key/OAuth2 auth support
  - Cursor pagination enforcement
  - Standard error envelope validation
  - Request ID header requirements
  - Breaking change detection with MAJOR severity
- Strict public API policy (`preset.strict.public.yaml`)
  - OAuth2-only authentication
  - All breaking changes escalate to BLOCKER
  - Required operationId and tags
  - URL versioning enforcement
- Breaking change detection engine
  - Removed operations/parameters/fields
  - Required/optional flips
  - Enum narrowing detection
  - Auth requirement changes
- Output artifact generation
  - `API_REVIEW.md` with severity-classified findings
  - `API_CHANGELOG.md` for spec diffs
  - `DEPRECATION_PLAN.md` for migration guidance
- CLI tool (`api-governor`)
- Python API for programmatic use
- JSON schema for policy validation
- Example OpenAPI specs (v1 baseline, v2 breaking)
- GitHub Actions CI/CD pipeline
- Docker support for containerized execution

### Documentation
- Comprehensive SKILL.md with procedure steps
- README with quick start guide
- CONTRIBUTING.md with development guidelines
- API documentation in `docs/`

## [0.1.0] - 2025-01-10

### Added
- Initial project structure
- Basic skill definition

[Unreleased]: https://github.com/akz4ol/api-governance-skill/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/akz4ol/api-governance-skill/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/akz4ol/api-governance-skill/releases/tag/v0.1.0
