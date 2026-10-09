# Plan: switch Bazaar to depend on jev-py-sdk

This is not done yet. Bazaar is unchanged.

1. **Add the dependency.** In `bazaar/pyproject.toml`:
   - add `jev-py-sdk @ https://github.com/ogarciarevett/jev-py-sdk/releases/download/v0.1.0/jev_py_sdk-0.1.0-py3-none-any.whl`;
   - for local work, add `[tool.uv.sources] jev-py-sdk = { path = "../jev-py-sdk", editable = true }`.
2. **Keep the decider in Bazaar.** The `BAZAAR_DECIDER=llm` switch depends on `bazaar_agent.llm`, so it
   stays there:
   - Shrink `bazaar_agent/jev/` to a shim. `__init__.py` re-exports `jev_sdk`, except for `judge`.
   - Wrap `judge` in `bazaar_agent/jev/judge.py`. When `decider() == "llm"`, it calls `jev_sdk.mask_request`
     and runs today's `_llm_result` path. Otherwise it calls `jev_sdk.judge`.
   - Keep `_own_options` and the two LLM reasons (`llm_unavailable`, `decider_call_cap`) in Bazaar.
     Export `BAZAAR_UNDECIDED_REASONS = (*jev_sdk.JEV_UNDECIDED_REASONS, ...)`.
   - Keep the `"decider": "llm"` key in decision lines by post-processing `jev_sdk.decision_line` in Bazaar.
3. **Log directory.** Set `JEV_DECISION_LOG_DIR=.local/jev-decisions` in Bazaar's environment, or pass
   `directory=` explicitly, so existing logs stay where they are.
4. **CLI default.** Bazaar's `python -m bazaar_agent.jev` keeps `--questions questions/negotiation.json` as
   its default and forwards the rest to `jev_sdk.__main__`.
5. **Tests.**
   - Delete `tests/jev/test_{judge,mask,log}.py`; they live in jev-py-sdk now.
   - Keep `tests/jev/test_decider.py`, plus a small test that the shim re-exports the SDK's public API.
6. **Vendored TS.** `vendor/jev-sdk` stays as it is. It is the parity reference, not a runtime dependency.
7. **Rollout.** Open one PR in Bazaar, run the full suite, and confirm a `--log` call writes
   byte-identical lines before and after the switch, apart from the timestamp.
