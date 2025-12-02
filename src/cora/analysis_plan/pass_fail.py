from __future__ import annotations

from typing import Iterable, List, Mapping, Sequence

from vapi.types.analysis_plan import AnalysisPlan
from vapi.types.success_evaluation_plan import SuccessEvaluationPlan

DEFAULT_RUBRIC = "PassFail"
DEFAULT_EVAL_MESSAGES: Sequence[Mapping[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are an expert call evaluator. You will be given a transcript "
            "of a call and the system prompt of the Ai participant. If the Ai "
            "successfully booked an appointment for the patient, label the "
            "call as `true`. If the patient answered but no appointment was "
            "scheduled, label the call as `false`. If a voicemail was left or "
            "the patient did not answer, label the call as `false`.\n\nRubric:\n\n"
            "{{rubric}}\n\nOnly respond with the evaluation result."
        ),
    },
    {
        "role": "user",
        "content": (
            "Here is the transcript of the call:\n\n{{transcript}}\n\n. Here "
            "is the ended reason of the call:\n\n{{endedReason}}\n\n"
        ),
    },
    {
        "role": "user",
        "content": "Here was the system prompt of the call:\n\n{{systemPrompt}}\n\n",
    },
]


def pass_fail_plan(
    *,
    rubric: str = DEFAULT_RUBRIC,
    evaluation_messages: Iterable[Mapping[str, str]] | None = None,
) -> AnalysisPlan:
    """
    Build the AnalysisPlan + SuccessEvaluationPlan pair used by assistants.
    Callers can override the rubric or even provide a different set of
    evaluation messages, while the defaults mirror the previous inline config.
    """

    messages: List[Mapping[str, str]] = (
        list(evaluation_messages) if evaluation_messages is not None else list(DEFAULT_EVAL_MESSAGES)
    )

    return AnalysisPlan(
        success_evaluation_plan=SuccessEvaluationPlan(
            rubric=rubric,
            messages=messages,
        )
    )
