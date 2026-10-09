# Parity with the TypeScript jev-sdk

Compared against jev-sdk `e155652f` (the copy vendored in Bazaar).

## Ported, with matching tests

| TS module | Python | Tests |
| --- | --- | --- |
| `judge.ts` | `jev_sdk.judge` | `test_judge.py`, `test_parity_ts.py` |
| `mask.ts` + the redaction list from `public-text-sanitizer.ts` | `jev_sdk.mask` | `test_mask.py` |
| `decision-log.ts` | `jev_sdk.log` | `test_log.py`, `test_parity_ts.py` |
| `jev-judge.ts` (CLI) | `jev judge` / `python -m jev_sdk judge` | `test_judge.py`, `test_parity_ts.py` |
| `jev-report.ts` (CLI) | `jev report` | `test_judge.py` |
| `questions/*.json` | `jev_sdk/questions/*.json` (bundled) | `test_question_packs.py` |

Request bodies, decision lines and digests are byte-compatible with the TS SDK (`js_json_dumps`
writes what `JSON.stringify` writes), so either SDK can read the other's logs.

## In the TS SDK, missing from the Python port

None of these were implemented in this milestone.

| TS | What it does | Notes |
| --- | --- | --- |
| `score-options.ts`, `jev-score-options.ts` (27 tests) | Composite scoring: one `score` question per dimension per option, weighted in code, with a margin rule for naming a winner | Single `score` verdicts are ported. The composite table is not. |
| `jev-outcome.ts` (CLI, 13 tests) | Records an outcome line from the shell | `outcome_line` and `append_line` exist in Python; only the subcommand is missing. |
| `jev-mcp-server.ts` (10 tests) | MCP server exposing judge/report to agents | |
| `jev-stop-hook.ts` | Claude Code stop hook that asks Jev whether the work is done | |
| `jev-smoke.ts` | Live smoke call against the real endpoint | |
| `capabilities.ts`, `jev-capabilities.ts` (43 tests) | Describes what the SDK and its question packs can judge | |
| `finding.ts`, `jev-finding.ts` (42 tests) | Routes a code-review finding through `finding_is_real` / `finding_is_pre_existing` | Uses git (`git show HEAD:<path>`). |
| `public-text-sanitizer.ts` as a public module | Sanitizes text for public reports | Its redaction list is inside `mask.py` (`redact_prohibited_values`, `prohibited_public_value_label`), but there is no public API for it. |
| `cli.ts` (9 tests) | The shared flag parser | Python uses `argparse`, so these tests have no equivalent. |
| `skills/jev/` | The agent skill (SKILL.md and references) | Docs only, not code. |

## Behavior differences

- The CLI requires `--questions`. It accepts a file path or a bundled pack name, and there is no
  consumer-relative default pack.
- The decision log defaults to `.jev/decisions` (TS: `.local/jev-decisions`).
  `$JEV_DECISION_LOG_DIR` moves it.
- The TS CLI test "does not load the consumer cwd .env implicitly" holds trivially: nothing in the
  Python package reads `.env`.
