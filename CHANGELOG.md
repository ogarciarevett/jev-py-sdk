# Changelog

All notable changes to jev-py-sdk are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/); see [docs/versioning.md](docs/versioning.md) for what
counts as the public API and which number each kind of change bumps.

## [Unreleased]

## [0.2.0] - 2026-10-23

Support for the experimental TypeSafe image models and Jev 1.14. Images and Box questions are
"dreamer-ready" upstream: the request format, answers and limits can change between releases.

### Added

- `judge(..., images={reference: png_or_jpeg_bytes})` sends images as request `assets`. Write the
  reference in the state, the instructions or the criteria where the image belongs. Only PNG and
  JPEG bytes are accepted, and every reference must survive masking. Image bytes are sent as they
  are (they are not text, so they are not masked) and are never written to the decision log.
- The `box` question type (Jev 1.14): a decided verdict is `"box"`, its value is the confidence, and
  `Verdict.box` holds the `top`, `bottom`, `left` and `right` edges as fractions of the image.
- `JEV_BOX_MODEL` (`jev-1.14.0`) and a `model` parameter on `judge` and `mask_request`. A box needs
  `jev-1.14.0` or `jev-preview`.
- The `TypeSafe-Danger-Zone-Images: true` header, sent automatically with every request that has an
  image or a box question.
- `long_context=True` sends `TypeSafe-Danger-Zone-Long-Context: true` and raises the state budget
  from 96,000 to 786,000 characters (262k tokens).
- `decision_line(..., images=..., long_context=...)` checks the references of a call that sent images
  and accepts the larger state of a long context call.

### Changed

- `JEV_QUESTION_TYPES` now includes `box`, and `Verdict` has a new `box` field. Under the 0.x policy
  that is a minor release: consumers that branch on the question type or the verdict fields should
  handle `box`.

### Added (unreleased before 0.2.0)

- `docs/versioning.md`: the versioning policy and release steps.
- `tests/test_versioning.py`: snapshots of the public API and behavioral constants, plus version and
  changelog consistency checks. The release workflow refuses a tag with no changelog section.

### Changed (unreleased before 0.2.0)

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

[Unreleased]: https://github.com/ogarciarevett/jev-py-sdk/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ogarciarevett/jev-py-sdk/releases/tag/v0.2.0
[0.1.0]: https://github.com/ogarciarevett/jev-py-sdk/releases/tag/v0.1.0
