# jev-py-sdk

Typed Jev judgments (`noul` / `choice` / `score`) from [TypeSafe](https://typesafe.ai), masked before
they leave your machine. This is the Python port of the TypeScript `jev-sdk`. It needs Python 3.10+ and
depends only on `httpx`.

## Install

```bash
pip install "jev-py-sdk @ https://github.com/ogarciarevett/jev-py-sdk/releases/download/v0.1.0/jev_py_sdk-0.1.0-py3-none-any.whl"
```

Each GitHub Release carries the wheel and a `SHA256SUMS` file. Nothing is published to PyPI yet.

To install the Aion 2 copilot, which brings this SDK with it, on a clean Windows PC:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/ogarciarevett/aion-copilot/main/scripts/install.ps1 | iex"
```

## Quickstart

```python
from jev_sdk import judge

state = {"ticket": "Checkout returns 502 after the deploy", "retries": 3, "owner_paged": False}
questions = {
    "needs_owner": {"type": "noul", "stakes": "design", "instructions": "Does the service owner have to act now?"},
    "failure_layer": {
        "type": "choice",
        "stakes": "passive",
        "instructions": "Which layer most likely failed?",
        "criteria": {"frontend": "UI or CDN", "api": "the HTTP service", "data": "database or cache"},
    },
    "risk": {
        "type": "score",
        "instructions": "How risky is waiting an hour?",
        "criteria": ["nobody notices the wait", "some users retry and succeed", "orders are lost while we wait"],
    },
}
result = judge(state, questions)  # reads $TYPESAFE_API_KEY
for question_id, verdict in result.verdicts.items():
    print(question_id, verdict.verdict, verdict.value, verdict.reason or "")
```

From a shell (`python -m jev_sdk` is the same command):

```bash
echo '{"decision": "ship"}' | jev judge --state - --questions plan-decisions --log
jev report
```

## Invariants

- **A verdict informs a move; it never authorizes one.** Your code decides, and its own guardrails still apply.
- **Everything is masked before it leaves the machine.** The state, the instructions and the criteria all go
  through `mask_state` / `mask_questions`. The decision log stores only the masked questions and a SHA-256
  digest of the masked state, never the state itself.
- **Every failure is the verdict `undecided` with a reason, never an exception.** That covers a missing key,
  a timeout, a network or HTTP error, a malformed body, an absent answer and a confidence below the bar
  (`JEV_UNDECIDED_REASONS`). Only a caller mistake, such as a malformed question, raises `JevUsageError`.
- **Stakes set the bar:** `passive` 0.6, `design` 0.75, `critical` 0.9. A question without stakes uses 0.8.
  An explicit `thresholds={...}` wins over both.

## Masking guarantees

`mask_text` normalizes the text (NFKC) and replaces each of these, whole, with `[redacted]`:

- e-mail addresses;
- connection strings (`postgres://`, `redis://`, `mongodb+srv://`, …);
- API-key shapes (`sk-…`, `ghp_…`, `github_pat_…`, `xox?-…`, `tskey-…`, `sk_live_…`);
- `Bearer` tokens and JWTs;
- PEM private keys, including an unterminated block;
- `key=value` credentials (`api_key`, `secret`, `token`, `password`, `passphrase`, `private_key`, `signing_key`);
- URLs with user:password;
- internal hostnames (`localhost`, RFC 1918 addresses, `*.internal`, `*.local`);
- account, party, contract, database and command ids.

Control characters become spaces. If anything recognizable survives the pass, the whole string becomes
`[redacted]` (fail closed).

In structured state:

- every string value is masked;
- numbers and booleans are kept;
- a field whose *name* contains a credential word (`token_value`, `client_secret_id`, `cookie`, …) has its value replaced, whatever that value is;
- a field name that itself looks like a credential is renamed `[redacted]#<n>`.

`stakes` never reaches the model.

## Decision log

Pass `--log` to the CLI, or write lines yourself with `decision_line` / `outcome_line` / `append_line`. The
log is one JSONL file per UTC day in `.jev/decisions/` under the working directory. Set
`JEV_DECISION_LOG_DIR` or pass `--directory` to move it. The line format matches the TypeScript SDK's, so
either SDK's report can read the other's logs.

## Development

```bash
uv sync
uv run pytest --cov      # offline: httpx.MockTransport only
uv run ruff check . && uv run black --check . && uv run mypy src tests
```

See [docs/parity.md](docs/parity.md) for what the TypeScript SDK has that this port does not, and
[PROVENANCE.md](PROVENANCE.md) for where the code came from.

## License

MIT, see [LICENSE](LICENSE).
