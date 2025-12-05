from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from vapi.types.analysis_plan import AnalysisPlan
from vapi.types.success_evaluation_plan import SuccessEvaluationPlan

DEFAULT_SUCCESS_EVAL_MESSAGES: Sequence[Mapping[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are an expert call evaluator. You will be given a transcript of a call and the system "
            "prompt of the AI participant. Determine if the call was successful based on the objectives "
            "inferred from the system prompt. DO NOT return anything except the result.\n\nRubric:\n"
            "{{rubric}}\n\nOnly respond with the result."
        ),
    },
    {
        "role": "user",
        "content": "Here is the transcript:\n\n{{transcript}}\n\n",
    },
    {
        "role": "user",
        "content": (
            "Here was the system prompt of the call:\n\n{{systemPrompt}}\n\n. Here is the ended "
            "reason of the call:\n\n{{endedReason}}\n\n"
        ),
    },
]


def success_evaluation_plan(
    *,
    rubric: str = "PassFail",
    messages: Iterable[Mapping[str, str]] | None = None,
    enabled: bool = True,
    timeout_seconds: float | None = None,
    min_messages_threshold: float | None = None,
) -> AnalysisPlan:
    """
    Build an AnalysisPlan that only evaluates the call outcome with the provided rubric.
    """

    resolved_messages = list(messages) if messages is not None else list(DEFAULT_SUCCESS_EVAL_MESSAGES)
    return AnalysisPlan(
        min_messages_threshold=min_messages_threshold,
        success_evaluation_plan=SuccessEvaluationPlan(
            rubric=rubric,
            messages=resolved_messages,
            enabled=enabled,
            timeout_seconds=timeout_seconds,
        ),
    )
