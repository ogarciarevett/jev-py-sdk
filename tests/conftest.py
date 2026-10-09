"""Every test runs offline and without the caller's TypeSafe key or decision-log location."""

from __future__ import annotations

import socket
from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def _offline(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.delenv("JEV_DECISION_LOG_DIR", raising=False)

    def refuse(*_args: object, **_kwargs: object) -> socket.socket:
        raise AssertionError("tests never open a real socket; use httpx.MockTransport")

    monkeypatch.setattr(socket, "create_connection", refuse)
    yield
