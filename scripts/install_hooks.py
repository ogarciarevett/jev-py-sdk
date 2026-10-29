"""Install this repository's shared pre-push entry point."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    subprocess.run(["git", "-C", str(ROOT), "config", "--local", "core.hooksPath", ".githooks"], check=True)
