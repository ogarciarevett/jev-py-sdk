# Coding standards

Python support remains >=3.10. Black 26.10.1 is the formatter of record; Ruff 0.14.3 lints. Keep the existing Python 3.10 target and 120-column configuration in `pyproject.toml`; do not add a second formatter. Tool versions are pinned in the development group and `uv.lock`.

Use `uv sync --locked` followed by `uv run --locked python scripts/check.py`. This non-writing gate runs Black `--check`, Ruff lint, existing strict mypy checks, and the offline suite with its existing 94% coverage requirement. Pre-push, CI and release share the gate; a nonzero exit stops later checks/build/publication. The existing OS/Python test matrix and offline CLI smoke remain required.

Follow the official linked-stack review/merge rule in [CONTRIBUTING.md](CONTRIBUTING.md). Preserve provider/API behavior, minimum runtime, typing and least-privilege workflow permissions. Keep baseline mechanical formatting separate from functional gate changes. Never restore the legacy evidence workflow or archived cross-AI template.

## Coordinator work queue

This is coordinator procedure, not an automated SDK runtime feature. Each coordinator reads its GitHub queue every loop: open issues matching its configured owner label, `ready-for-agent`, and `P0` or `P1`, with P0 first. Skip issues with live `Agent:` claims.

Every P0 specification has one `implement-spec` lead who owns the frontier until the whole specification closes. The next eligible lead starts in the same turn. At start the lead writes `Agent:<name>` and sends the Chief `STARTED: #<number> <agent>`. The lead replaces the claim when finishing. A specification-creation task is complete only after its authorized lead has started.
