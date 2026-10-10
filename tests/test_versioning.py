"""Guards for the version number: a public API change can't slip into a release unnoticed.

If a test here fails because you changed the public API on purpose, follow docs/versioning.md:
update the snapshot below, add a CHANGELOG entry under [Unreleased], and bump the version when you
release (minor for a breaking change while 0.x, patch for an addition).
"""

from __future__ import annotations

import re
from pathlib import Path

import jev_sdk

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_API = frozenset(
    {
        "JEV_API_KEY_VARIABLE",
        "JEV_DECISION_LOG_DIRECTORY",
        "JEV_DECISION_LOG_VARIABLE",
        "JEV_DEFAULT_THRESHOLD",
        "JEV_DEFAULT_TIMEOUT_S",
        "JEV_ENDPOINT",
        "JEV_MODEL",
        "JEV_OUTCOMES",
        "JEV_QUESTION_TYPES",
        "JEV_REDACTION",
        "JEV_STAKES",
        "JEV_STAKES_THRESHOLDS",
        "JEV_UNDECIDED",
        "JEV_UNDECIDED_REASONS",
        "JevUsageError",
        "JudgeResult",
        "MaskedRequest",
        "QuestionTally",
        "Verdict",
        "__version__",
        "append_line",
        "bundled_pack_names",
        "call_digest",
        "decision_line",
        "iso_now",
        "js_json_dumps",
        "judge",
        "load_bundled_questions",
        "load_questions",
        "log_date",
        "log_tally",
        "mask_questions",
        "mask_request",
        "mask_state",
        "mask_text",
        "masked_digest",
        "outcome_line",
        "questions_from_text",
        "read_log",
        "report_json",
        "report_table",
        "resolve_log_directory",
        "state_from_text",
        "threshold_for",
    }
)

BEHAVIORAL_CONSTANTS = {
    "JEV_UNDECIDED_REASONS": (
        "typesafe_api_key_missing",
        "request_timeout",
        "network_error",
        "http_client_error",
        "http_server_error",
        "rate_limited",
        "response_schema_mismatch",
        "answer_missing",
        "answer_type_mismatch",
        "below_threshold",
    ),
    "JEV_STAKES_THRESHOLDS": {"passive": 0.6, "design": 0.75, "critical": 0.9},
    "JEV_DEFAULT_THRESHOLD": 0.8,
    "JEV_MODEL": "jev-latest",
    "JEV_ENDPOINT": "https://api.typesafe.ai/v1/systemone",
    "JEV_UNDECIDED": "undecided",
    "JEV_QUESTION_TYPES": ("noul", "choice", "score"),
    "JEV_STAKES": ("passive", "design", "critical"),
    "JEV_OUTCOMES": ("right", "wrong", "unknown"),
    "JEV_DECISION_LOG_DIRECTORY": ".jev/decisions",
    "JEV_DECISION_LOG_VARIABLE": "JEV_DECISION_LOG_DIR",
    "JEV_API_KEY_VARIABLE": "TYPESAFE_API_KEY",
}


def project_version() -> str:
    """The [project] version from pyproject.toml (a regex: tomllib only exists from Python 3.11)."""
    found = re.search(r'^version = "([^"]+)"$', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M)
    assert found, "pyproject.toml has no version"
    return found.group(1)


def test_the_public_api_matches_the_snapshot() -> None:
    exported = frozenset(jev_sdk.__all__)
    added, removed = sorted(exported - PUBLIC_API), sorted(PUBLIC_API - exported)
    assert not added and not removed, (
        f"public API changed (added {added}, removed {removed}): see docs/versioning.md, "
        "update PUBLIC_API, add a CHANGELOG entry and bump the version on release"
    )


def test_every_exported_name_exists() -> None:
    missing = [name for name in jev_sdk.__all__ if not hasattr(jev_sdk, name)]
    assert missing == []


def test_behavioral_constants_match_the_snapshot() -> None:
    for name, expected in BEHAVIORAL_CONSTANTS.items():
        actual = getattr(jev_sdk, name)
        actual = dict(actual) if isinstance(expected, dict) else actual
        assert actual == expected, f"{name} changed: a behavioral change needs a version bump (docs/versioning.md)"


def test_the_installed_version_is_the_pyproject_version() -> None:
    assert jev_sdk.__version__ == project_version()


def test_the_version_is_plain_semver() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", project_version())


def test_the_changelog_has_a_section_for_the_current_version_and_an_unreleased_one() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    version = project_version()
    assert "## [Unreleased]" in changelog
    assert re.search(
        rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$", changelog, re.M
    ), f"CHANGELOG.md has no dated section for {version}"
    assert f"[{version}]: https://github.com/ogarciarevett/jev-py-sdk/releases/tag/v{version}" in changelog
