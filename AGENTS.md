# Agent instructions

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [CODING_STANDARDS.md](CODING_STANDARDS.md), including their contributor, license and review requirements.

Install the repository hook with `uv run --locked python scripts/install_hooks.py`; run `uv run --locked python scripts/check.py` before pushing. Do not bypass a failing gate. Report exact heads, commands/results, and unrun checks honestly.

Related or dependent feature PRs must use official `gh stack`, record base/head relationships, and merge together via `gh stack merge`. Return **CHANGES** for missing linkage; do not approve or merge dependent slices alone. Independent changes do not require a stack.

Coordinators must follow the [GitHub queue, claim and STARTED procedure](CODING_STANDARDS.md#coordinator-work-queue), including the single-lead rule for P0 specifications. This guidance does not implement a runtime scheduler.
