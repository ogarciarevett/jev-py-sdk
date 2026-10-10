# Versioning and releases

jev-py-sdk follows [Semantic Versioning 2.0.0](https://semver.org/). Consumers depend on it, so a
version number is a promise: it says what an upgrade can break.

## What the public API is

Everything a consumer can rely on is covered by the version number:

1. **Python names** exported in `jev_sdk.__all__`, and their signatures and return types.
2. **Wire and file formats**, which must stay byte-compatible with the TypeScript jev-sdk:
   - the request body sent to TypeSafe;
   - `Verdict.to_dict()` / `JudgeResult.to_json()`;
   - the decision-log line format (`decision_line`, `outcome_line`);
   - the question-pack format.
3. **Constants with behavioral meaning**:
   - `JEV_UNDECIDED_REASONS`;
   - the stakes thresholds (`passive` 0.6, `design` 0.75, `critical` 0.9);
   - `JEV_DEFAULT_THRESHOLD`, `JEV_MODEL`, `JEV_ENDPOINT`;
   - `JEV_DECISION_LOG_DIRECTORY` and `JEV_DECISION_LOG_VARIABLE`.
4. **The `jev` CLI**: subcommands, flags, exit codes (0 for any verdict, 2 for a usage error), and
   the JSON it prints.
5. **The invariants**:
   - a verdict never authorizes a move;
   - everything is masked before it leaves the machine;
   - every failure is `undecided` with a reason, never an exception (except `JevUsageError` for a
     caller mistake).

Private modules and names (leading underscore, or anything outside `__all__`) can change in any
release.

`tests/test_versioning.py` snapshots items 1 and 3. Changing any of them fails the suite until the
snapshot, `CHANGELOG.md` and the version are updated together.

## Which number to bump

While the version is **0.x**, the minor number plays the role of the major one:

| Change | 0.x (now) | ≥ 1.0 |
| --- | --- | --- |
| Breaking: remove or rename a public name, change a signature, a format, a reason code, a default threshold, or CLI behavior | **minor** (0.1 → 0.2) | **major** |
| Backward-compatible addition: a new export, an optional parameter, a new bundled pack, a new CLI flag | **patch** (0.1.0 → 0.1.1) | **minor** |
| Bug fix, docs, tests, tooling, with no API change | **patch**, or no release at all | **patch** |
| A new undecided reason or a new verdict field | **minor** (consumers branch on them) | **major** |

Consumers should pin to the compatible range. For example, claude-companion declares
`jev-py-sdk>=0.1,<0.2`, which takes patch releases and never a breaking minor.

Version 1.0.0 is cut once the TS parity gaps in `docs/parity.md` that we intend to close are closed.

## Releasing

1. Move the entries under `## [Unreleased]` in `CHANGELOG.md` to a new `## [X.Y.Z] - YYYY-MM-DD`
   section, and update the compare links at the bottom.
2. Set `version = "X.Y.Z"` in `pyproject.toml`. `jev_sdk.__version__` reads it from the package
   metadata, so there is no second place to edit.
3. If the public API changed, update the snapshot in `tests/test_versioning.py`.
4. Open a PR, let CI pass (lint, mypy, tests on 3.10/3.12/3.13 for Linux and Windows), and merge it.
5. Tag the merge commit on `main` and push the tag:

   ```bash
   git tag -a vX.Y.Z -m "jev-py-sdk X.Y.Z"
   git push origin vX.Y.Z
   ```

   The `release` workflow:
   - re-runs the tests;
   - refuses a tag that differs from `pyproject.toml` or has no `CHANGELOG.md` section;
   - builds the wheel and sdist, writes `SHA256SUMS`, and publishes a GitHub Release marked latest.

**Never** move or re-push a tag, and never replace the assets of a published release: consumers
verify them by SHA-256. A mistake gets a new patch version.

Publishing to PyPI is not set up yet; GitHub Releases are the distribution channel.
