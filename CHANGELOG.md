# Changelog

All notable changes to jev-py-sdk are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/); see [docs/versioning.md](docs/versioning.md) for what
counts as the public API and which number each kind of change bumps.

## [Unreleased]

### Added

- `docs/versioning.md`: the versioning policy and release steps.
- `tests/test_versioning.py`: snapshots of the public API and behavioral constants, plus version and
  changelog consistency checks. The release workflow refuses a tag with no changelog section.

### Changed

- README: the claude-companion install command now starts from a public bootstrap gist, because that
  repository is private. Docs only, no code change.

## [0.1.0] - 2026-10-09

### Added

- First standalone release, extracted from bazaar's `bazaar_agent.jev` at `5b23710` (see
  `PROVENANCE.md`).
- `judge()` for `noul`, `choice` and `score` questions, with stakes thresholds `passive` 0.6,
  `design` 0.75 and `critical` 0.9.
- Masking of state, instructions and criteria before they leave the machine.
- The decision log (`.jev/decisions`, configurable with `$JEV_DECISION_LOG_DIR`).
- The `jev` CLI (also `python -m jev_sdk`).
- The bundled `agent-operations` and `plan-decisions` question packs.
- Python 3.10+, with `httpx` as the only runtime dependency.

[Unreleased]: https://github.com/ogarciarevett/jev-py-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ogarciarevett/jev-py-sdk/releases/tag/v0.1.0
