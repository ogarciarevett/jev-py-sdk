"""Images, Box questions and the long context header (Jev 1.14). No live network: httpx.MockTransport only."""

from __future__ import annotations

import base64
import json
from typing import Any

import httpx
import pytest

from jev_sdk import JEV_BOX_MODEL, JEV_MODEL, JevUsageError, decision_line, judge, mask_request

KEY = "-".join(["fixture", "key", "value", "0003"])
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
PHOTO = "3f0c9a52-photo"
BOX_QUESTIONS = {"mug": {"type": "box", "instructions": "the coffee mug in `photo`"}}
EDGES = {"top": 0.25, "bottom": 0.82, "left": 0.44, "right": 0.84}


class Capture:
    def __init__(self, answers: dict[str, Any]) -> None:
        self.answers = answers
        self.requests: list[httpx.Request] = []

    def transport(self) -> httpx.MockTransport:
        def handle(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return httpx.Response(200, json={"model": "jev-1.14.0", "answers": self.answers})

        return httpx.MockTransport(handle)

    def body(self) -> dict[str, Any]:
        parsed: dict[str, Any] = json.loads(self.requests[0].content)
        return parsed


def box_judge(answer: object, **options: Any) -> tuple[Capture, Any]:
    capture = Capture({"mug": answer})
    options.setdefault("images", {PHOTO: PNG})
    options.setdefault("model", JEV_BOX_MODEL)
    result = judge({"photo": PHOTO}, BOX_QUESTIONS, api_key=KEY, transport=capture.transport(), **options)
    return capture, result.verdicts["mug"]


def test_a_box_is_decided_with_its_edges_and_sends_the_images_header() -> None:
    capture, verdict = box_judge({"type": "box", "box": EDGES, "confidence": 0.92})
    assert verdict.decided and verdict.verdict == verdict.leaning == "box"
    assert verdict.value == 0.92 and verdict.value_kind == "confidence"
    assert dict(verdict.box) == EDGES
    assert verdict.to_dict()["box"] == EDGES
    request = capture.requests[0]
    assert request.headers["typesafe-danger-zone-images"] == "true"
    assert "typesafe-danger-zone-long-context" not in request.headers
    body = capture.body()
    assert list(body) == ["state", "model", "questions", "assets"]
    assert body["model"] == "jev-1.14.0"
    assert body["assets"] == {PHOTO: {"type": "image", "format": "png", "data_base64": base64.b64encode(PNG).decode()}}


def test_a_box_below_the_bar_is_undecided_but_keeps_its_edges() -> None:
    _, verdict = box_judge({"type": "box", "box": EDGES, "confidence": 0.4})
    assert verdict.verdict == "undecided" and verdict.reason == "below_threshold"
    assert dict(verdict.box) == EDGES


@pytest.mark.parametrize(
    "edges",
    [
        {"top": 0.5, "bottom": 0.4, "left": 0.1, "right": 0.2},
        {"top": 0.1, "bottom": 0.4, "left": 0.3, "right": 0.3},
        {"top": 0.1, "bottom": 1.4, "left": 0.1, "right": 0.2},
        {"top": 0.1, "bottom": 0.4, "left": 0.1},
        None,
    ],
)
def test_a_malformed_box_is_a_schema_mismatch(edges: object) -> None:
    _, verdict = box_judge({"type": "box", "box": edges, "confidence": 0.95})
    assert verdict.reason == "response_schema_mismatch" and verdict.box is None


def test_an_image_in_a_text_question_sends_a_jpeg_asset_and_the_header() -> None:
    capture = Capture({"same": {"type": "noul", "noul": 0.97}})
    questions = {"same": {"type": "noul", "instructions": "Is `photo` the same dog as this one: 77b0d4a1-poster?"}}
    images = {PHOTO: PNG, "77b0d4a1-poster": JPEG}
    result = judge({"photo": PHOTO}, questions, api_key=KEY, images=images, transport=capture.transport())
    assert result.verdicts["same"].verdict == "yes"
    assert capture.body()["model"] == JEV_MODEL
    assert capture.body()["assets"]["77b0d4a1-poster"]["format"] == "jpg"
    assert capture.requests[0].headers["typesafe-danger-zone-images"] == "true"


def test_a_text_only_request_is_unchanged() -> None:
    capture = Capture({"q": {"type": "noul", "noul": 0.9}})
    judge("state", {"q": {"type": "noul", "instructions": "Is it?"}}, api_key=KEY, transport=capture.transport())
    assert list(capture.body()) == ["state", "model", "questions"]
    assert "typesafe-danger-zone-images" not in capture.requests[0].headers


def test_long_context_sends_its_header_and_raises_the_state_budget() -> None:
    questions = {"q": {"type": "noul", "instructions": "Is it?"}}
    big = "word " * 30_000
    with pytest.raises(JevUsageError, match="larger than 96000"):
        mask_request(big, questions)
    capture = Capture({"q": {"type": "noul", "noul": 0.9}})
    judge(big, questions, api_key=KEY, long_context=True, transport=capture.transport())
    assert capture.requests[0].headers["typesafe-danger-zone-long-context"] == "true"


@pytest.mark.parametrize(
    ("images", "questions", "message"),
    [
        ({PHOTO: b"GIF89a"}, BOX_QUESTIONS, "only PNG and JPEG"),
        ({"unused-ref": PNG, PHOTO: PNG}, BOX_QUESTIONS, "does not appear"),
        ({"": PNG}, BOX_QUESTIONS, "non-empty"),
        ({PHOTO: PNG}, {"mug": {"type": "box", "instructions": "the mug", "criteria": ["a", "b"]}}, "no criteria"),
    ],
)
def test_caller_mistakes_with_images_raise(images: Any, questions: Any, message: str) -> None:
    with pytest.raises(JevUsageError, match=message):
        mask_request({"photo": PHOTO}, questions, images=images)


def test_a_reference_the_masking_rewrites_is_refused() -> None:
    reference = "user@example.com"
    with pytest.raises(JevUsageError, match="does not appear"):
        mask_request({"photo": reference}, BOX_QUESTIONS, images={reference: PNG})


def test_an_empty_model_is_refused() -> None:
    with pytest.raises(JevUsageError, match="model"):
        mask_request("state", {"q": {"type": "noul", "instructions": "Is it?"}}, model=" ")


def test_the_decision_line_never_holds_the_image_bytes() -> None:
    capture = Capture({"mug": {"type": "box", "box": EDGES, "confidence": 0.92}})
    result = judge(
        {"photo": PHOTO},
        BOX_QUESTIONS,
        api_key=KEY,
        images={PHOTO: PNG},
        model=JEV_BOX_MODEL,
        transport=capture.transport(),
    )
    line = decision_line({"photo": PHOTO}, BOX_QUESTIONS, result, "2026-10-23T00:00:00.000Z", images={PHOTO: PNG})
    assert base64.b64encode(PNG).decode() not in line
    assert json.loads(line)["verdicts"]["mug"]["box"] == EDGES
