# Provenance

This package was extracted from the Python port inside `bazaar`. The files were copied, not
history-filtered: a full clone of `bazaar` was impractical, and the port's history there is mostly
Bazaar integration work.

- Source: https://github.com/claude-hackaton-madrid-team-1/bazaar
- Commit: `5b23710287fb652ac9f166336023d1ff05e65c97`
- Copied:
  - `src/bazaar_agent/jev/{__init__,__main__,judge,mask,log}.py` → `src/jev_sdk/`
  - `tests/jev/test_{judge,log,mask}.py` → `tests/`
  - `vendor/jev-sdk/questions/*.json` → `src/jev_sdk/questions/`
- Upstream of the port: the TypeScript `jev-sdk` (https://github.com/ogarciarevett/jev-sdk, private),
  commit `e155652fabf81d87ed9db8e3f4ef1e9b0a314c09`, as pinned in Bazaar's `vendor/jev-sdk/VENDORED.md`.

## Changes made during extraction

- Renamed the imports `bazaar_agent.jev` → `jev_sdk`.
- Removed the `BAZAAR_DECIDER=llm` switch: `decider.py`, `_llm_result` and `_own_options` in `judge.py`,
  the `llm_unavailable` and `decider_call_cap` undecided reasons, the `"decider"` key in decision lines,
  and `tests/jev/test_decider.py`. These depend on `bazaar_agent.llm` and stay in Bazaar
  (see `docs/bazaar-migration.md`).
- The decision-log directory is now `.jev/decisions`, overridable with `$JEV_DECISION_LOG_DIR` or
  `--directory` (`resolve_log_directory`). It was `.local/jev-decisions`.
- The CLI no longer defaults to Bazaar's `questions/negotiation.json`. `--questions` is required, and it
  also accepts a bundled pack name (`bundled_pack_names`, `load_bundled_questions`).
- Python 3.10 support: `JsonValue` is a `TypeAlias` instead of a PEP 695 `type` statement, and the code
  uses `timezone.utc` instead of `datetime.UTC`.
- New tests: `test_question_packs.py` and `test_parity_ts.py` (TS cases the port did not cover), plus a
  conftest that blocks real sockets.
