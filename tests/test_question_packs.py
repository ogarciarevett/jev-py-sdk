"""Port of jev-sdk test/jev-question-pack.test.ts: every shipped pack is a valid Jev request."""

from __future__ import annotations

import json
from importlib import resources

import pytest

from jev_sdk import bundled_pack_names, load_bundled_questions, mask_request


def test_the_two_upstream_packs_ship_with_the_package() -> None:
    assert set(bundled_pack_names()) >= {"agent-operations", "plan-decisions"}


@pytest.mark.parametrize("name", bundled_pack_names())
def test_every_shipped_pack_is_a_valid_jev_request(name: str) -> None:
    questions = load_bundled_questions(name)
    assert len(mask_request("sample", questions).questions) > 0


def test_finding_routing_gets_both_questions_from_separate_packs() -> None:
    folder = resources.files("jev_sdk") / "questions"
    operations = json.loads((folder / "agent-operations.json").read_text(encoding="utf-8"))
    plan = json.loads((folder / "plan-decisions.json").read_text(encoding="utf-8"))
    assert operations["questions"]["finding_is_real"]["type"] == "noul"
    assert plan["questions"]["finding_is_pre_existing"]["type"] == "noul"
