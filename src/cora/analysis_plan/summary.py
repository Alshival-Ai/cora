from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from vapi.types.analysis_plan import AnalysisPlan
from vapi.types.summary_plan import SummaryPlan

DEFAULT_SUMMARY_MESSAGES: Sequence[Mapping[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are an expert note-taker. You will be given a transcript of a call. "
            "Summarize the call in 2-3 sentences. DO NOT return anything except the summary."
        ),
    },
    {
        "role": "user",
        "content": (
            "Here is the transcript:\n\n{{transcript}}\n\n. Here is the ended reason of the call:\n\n"
            "{{endedReason}}\n\n"
        ),
    },
]


def summary_plan(
    *,
    messages: Iterable[Mapping[str, str]] | None = None,
    enabled: bool = True,
    timeout_seconds: float | None = None,
    min_messages_threshold: float | None = None,
) -> AnalysisPlan:
    """
    Build an AnalysisPlan that only enables the summary section. Callers can override the
    prompt messages, toggle the plan, or tweak the timeout without having to work with the
    underlying Vapi types directly.
    """

    resolved_messages = list(messages) if messages is not None else list(DEFAULT_SUMMARY_MESSAGES)
    return AnalysisPlan(
        min_messages_threshold=min_messages_threshold,
        summary_plan=SummaryPlan(
            enabled=enabled,
            messages=resolved_messages,
            timeout_seconds=timeout_seconds,
        ),
    )
