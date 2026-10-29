"""The shared golden vectors in conformance/vectors, run against this SDK.

These files are the canonical copy: jev-sdk (TypeScript) and jev-rs (Rust) run or compare against
them, so a changed vector fails every SDK until each one is updated. No live network.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from jev_sdk import JevUsageError, js_json_dumps, judge, mask_state, mask_text

VECTORS = Path(__file__).resolve().parent.parent / "conformance" / "vectors"
JUDGE = json.loads((VECTORS / "judge.json").read_text(encoding="utf-8"))
MASK = json.loads((VECTORS / "mask.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", MASK["text"], ids=lambda case: case["name"])
def test_mask_text_vector(case: dict[str, Any]) -> None:
    assert mask_text(case["raw"]) == case["masked"]


@pytest.mark.parametrize("case", MASK["state"], ids=lambda case: case["name"])
def test_mask_state_vector(case: dict[str, Any]) -> None:
    assert mask_state(case["raw"]) == case["masked"]


@pytest.mark.parametrize("case", JUDGE["cases"], ids=lambda case: case["name"])
def test_judge_vector(case: dict[str, Any]) -> None:
    sent: list[httpx.Request] = []
    reply = case.get("reply")

    def handle(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        if reply is None:
            return httpx.Response(599, content=b"{}")
        return httpx.Response(reply["status"], content=reply["body"].encode(), headers=reply["headers"])

    given = case["options"]
    options: dict[str, Any] = {
        "api_key": given.get("apiKey", JUDGE["apiKey"]),
        "transport": httpx.MockTransport(handle),
    }
    if "timeoutMs" in given:
        options["timeout_s"] = given["timeoutMs"] / 1000
    if "model" in given:
        options["model"] = given["model"]
    if "thresholds" in given:
        options["thresholds"] = given["thresholds"]
    expect = case["expect"]

    if expect.get("usageError"):
        with pytest.raises(JevUsageError):
            judge(case["state"], case["questions"], **options)
        assert len(sent) == expect["requests"]
        return

    result = judge(case["state"], case["questions"], **options)
    assert len(sent) == expect["requests"]
    if "body" in expect:
        assert sent[0].content.decode() == expect["body"]
    for name, value in expect.get("headers", {}).items():
        assert sent[0].headers.get(name) == value
    assert result.model == expect["model"]
    got = {key: verdict.to_dict() for key, verdict in result.verdicts.items()}
    assert js_json_dumps(got) == js_json_dumps(expect["verdicts"])
