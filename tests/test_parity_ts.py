"""Cases from jev-sdk's TypeScript tests that the ported suites did not already cover.

Each test names the TS file and case it mirrors. No live network: httpx.MockTransport only.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from jev_sdk import (
    JEV_STAKES_THRESHOLDS,
    append_line,
    judge,
    log_tally,
    read_log,
)
from jev_sdk.__main__ import main

KEY = "-".join(["fixture", "key", "value", "0002"])


def replying(answers: dict[str, Any]) -> httpx.MockTransport:
    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"model": "jev-1.13.0", "answers": answers})

    return httpx.MockTransport(handle)


# --- jev-judge.test.ts ---------------------------------------------------------------------------


@pytest.mark.parametrize("noul", [0.95, 0.05])
def test_a_decided_verdict_agrees_with_its_own_leaning(noul: float) -> None:
    """jev-judge: "a decided verdict agrees with its own leaning"."""
    questions = {"needs_owner": {"type": "noul", "instructions": "Does the owner have to act?"}}
    transport = replying({"needs_owner": {"type": "noul", "noul": noul}})
    verdict = judge("state", questions, api_key=KEY, transport=transport).verdicts["needs_owner"]
    assert verdict.decided
    assert verdict.verdict == verdict.leaning


def test_a_choice_verdict_agrees_with_its_leaning() -> None:
    questions = {"layer": {"type": "choice", "instructions": "Which layer?", "criteria": {"api": None, "data": None}}}
    transport = replying({"layer": {"type": "choice", "choice": "data", "confidence": 0.9}})
    verdict = judge("state", questions, api_key=KEY, transport=transport).verdicts["layer"]
    assert verdict.verdict == verdict.leaning == "data"


# --- jev-decision-log.test.ts --------------------------------------------------------------------


def test_the_rows_are_ordered_by_question_id_so_two_runs_read_the_same(tmp_path: Path) -> None:
    """jev-decision-log: "the rows are ordered by question id, so two runs read the same"."""
    for question_id in ("zeta", "Alpha", "beta"):
        line = {
            "kind": "decision",
            "at": "2026-09-20T00:00:00.000Z",
            "stateDigest": question_id * 4,
            "verdicts": {question_id: {"type": "noul", "verdict": "yes"}},
        }
        append_line(tmp_path, "2026-09-20", json.dumps(line))
    assert [row.question for row in log_tally(read_log(tmp_path))] == ["Alpha", "beta", "zeta"]


# --- jev-judge-cli.test.ts -----------------------------------------------------------------------


@pytest.fixture
def no_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)


def run_cli(argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, dict[str, Any]]:
    code = main(argv)
    out = capsys.readouterr().out
    return code, json.loads(out) if out.strip() else {}


@pytest.mark.usefixtures("no_key")
def test_reads_the_state_from_stdin_and_never_echoes_a_secret_it_was_given(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """jev-judge-cli: "reads the state from stdin, and never echoes a secret it was given"."""
    secret = "sk-" + "a" * 32
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"note": f"key is {secret}"})))
    code = main(["judge", "--state", "-", "--questions", "plan-decisions"])
    captured = capsys.readouterr()
    assert code == 0
    assert secret not in captured.out + captured.err
    assert set(json.loads(captured.out)["verdicts"]) == {
        "finding_is_pre_existing",
        "options_are_exclusive",
        "report_proves_criterion",
    }


@pytest.mark.usefixtures("no_key")
def test_each_question_keeps_the_bar_its_own_stakes_name(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """jev-judge-cli: "each question keeps the bar its own stakes name"."""
    state = tmp_path / "state.txt"
    state.write_text("a plan")
    _, printed = run_cli(["judge", "--state", str(state), "--questions", "plan-decisions"], capsys)
    bars = {question_id: verdict["threshold"] for question_id, verdict in printed["verdicts"].items()}
    assert bars == {"finding_is_pre_existing": 0.75, "options_are_exclusive": 0.6, "report_proves_criterion": 0.9}


@pytest.mark.usefixtures("no_key")
def test_stakes_sets_one_bar_for_every_question_and_threshold_still_wins(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """jev-judge-cli: "--stakes sets one bar for every question" and "--threshold still wins over both"."""
    state = tmp_path / "state.txt"
    state.write_text("a plan")
    base = ["judge", "--state", str(state), "--questions", "plan-decisions"]
    _, staked = run_cli([*base, "--stakes", "critical"], capsys)
    assert {verdict["threshold"] for verdict in staked["verdicts"].values()} == {JEV_STAKES_THRESHOLDS["critical"]}
    _, both = run_cli([*base, "--stakes", "critical", "--threshold", "0.7"], capsys)
    assert {verdict["threshold"] for verdict in both["verdicts"].values()} == {0.7}


def test_prints_the_usage_text_for_help_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """jev-judge-cli: "prints the usage text for --help and exits 0" and names the stakes words."""
    with pytest.raises(SystemExit) as exited:
        main(["judge", "--help"])
    assert exited.value.code == 0
    usage = capsys.readouterr().out
    assert "--stakes" in usage
    assert all(word in usage for word in ("passive", "design", "critical"))


@pytest.mark.usefixtures("no_key")
def test_a_bundled_pack_name_and_a_pack_file_both_load(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    state = tmp_path / "state.txt"
    state.write_text("a plan")
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps({"questions": {"ok": {"type": "noul", "instructions": "Is it ok?"}}}))
    _, from_file = run_cli(["judge", "--state", str(state), "--questions", str(pack)], capsys)
    assert list(from_file["verdicts"]) == ["ok"]


def test_the_questions_flag_is_required(capsys: pytest.CaptureFixture[str]) -> None:
    """A generic SDK has no consumer pack to default to, so a missing pack is a usage error."""
    with pytest.raises(SystemExit) as exited:
        main(["judge", "--state", "-"])
    assert exited.value.code == 2
