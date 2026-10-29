"""Shared non-writing quality gate for pre-push, CI and release."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    for arguments in (
        ("black", "--check", "."),
        ("ruff", "check", "."),
        ("mypy", "src", "tests"),
        ("pytest", "--cov"),
    ):
        command = ["uv", "run", "--locked", *arguments]
        print("+ " + " ".join(command), flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
