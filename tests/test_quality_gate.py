"""Exercise the installed hook at its external tool boundary without publishing."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(os.name == "nt", "POSIX executable tool fixtures; Windows product tests remain enabled")
class QualityGateTests(unittest.TestCase):
    def test_delivery_requires_every_check_to_succeed(self) -> None:
        for failed in ("", "black", "ruff", "mypy", "pytest"):
            with self.subTest(failed=failed), tempfile.TemporaryDirectory() as directory:
                repo = Path(directory)
                for name in ("scripts", ".githooks"):
                    shutil.copytree(ROOT / name, repo / name)
                subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
                subprocess.run([sys.executable, "scripts/install_hooks.py"], cwd=repo, check=True)
                tools = repo / "tools"
                tools.mkdir()
                uv = tools / "uv"
                uv.write_text(
                    f"#!{sys.executable}\n"
                    "import os, subprocess, sys\n"
                    "from pathlib import Path\n"
                    "tool = sys.argv[3]\n"
                    "if tool == 'python':\n"
                    "    raise SystemExit(subprocess.call([sys.executable, *sys.argv[4:]]))\n"
                    "with Path('checks.log').open('a') as log:\n"
                    "    log.write(tool + '\\n')\n"
                    "raise SystemExit(67 if tool == os.environ.get('FAIL_TOOL') else 0)\n"
                )
                uv.chmod(0o755)
                env = {**os.environ, "PATH": str(tools) + os.pathsep + os.environ["PATH"], "FAIL_TOOL": failed}
                result = subprocess.run(["git", "hook", "run", "pre-push"], cwd=repo, env=env, check=False)
                if result.returncode == 0:
                    (repo / "build-and-publish").touch()
                self.assertEqual(result.returncode, 67 if failed else 0)
                self.assertEqual((repo / "build-and-publish").exists(), not failed)
                expected = ["black", "ruff", "mypy", "pytest"]
                self.assertEqual(
                    (repo / "checks.log").read_text().splitlines(),
                    expected[: expected.index(failed) + 1] if failed else expected,
                )
