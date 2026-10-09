"""Jev: typed judgments (noul / choice / score) from TypeSafe, ported from the TypeScript jev-sdk.

A verdict informs a move; it never authorizes one. Everything is masked before it leaves the
machine, and every failure is the verdict `undecided` with a reason, never an exception.
"""

from importlib.metadata import PackageNotFoundError, version

from jev_sdk.judge import (
    JEV_API_KEY_VARIABLE,
    JEV_DEFAULT_THRESHOLD,
    JEV_DEFAULT_TIMEOUT_S,
    JEV_ENDPOINT,
    JEV_MODEL,
    JEV_STAKES_THRESHOLDS,
    JEV_UNDECIDED,
    JEV_UNDECIDED_REASONS,
    JevUsageError,
    JudgeResult,
    MaskedRequest,
    Verdict,
    bundled_pack_names,
    judge,
    load_bundled_questions,
    load_questions,
    mask_request,
    questions_from_text,
    state_from_text,
    threshold_for,
)
from jev_sdk.log import (
    JEV_DECISION_LOG_DIRECTORY,
    JEV_DECISION_LOG_VARIABLE,
    JEV_OUTCOMES,
    QuestionTally,
    append_line,
    call_digest,
    decision_line,
    iso_now,
    log_date,
    log_tally,
    outcome_line,
    read_log,
    report_json,
    report_table,
    resolve_log_directory,
)
from jev_sdk.mask import (
    JEV_QUESTION_TYPES,
    JEV_REDACTION,
    JEV_STAKES,
    js_json_dumps,
    mask_questions,
    mask_state,
    mask_text,
    masked_digest,
)

__all__ = [
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
]

try:
    __version__ = version("jev-py-sdk")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0.0.0"
