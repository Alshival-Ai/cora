from __future__ import annotations

from typing import Any, Iterable, Iterator, Mapping, MutableMapping, Sequence, Tuple

from vapi.types.analysis_plan import AnalysisPlan
from vapi.types.json_schema import JsonSchema
from vapi.types.structured_data_multi_plan import StructuredDataMultiPlan
from vapi.types.structured_data_plan import StructuredDataPlan

DEFAULT_STRUCTURED_DATA_MESSAGES: Sequence[Mapping[str, str]] = [
    {
        "role": "system",
        "content": (
            "You are an expert data extractor. You will be given a transcript of a call. "
            "Extract structured data per the JSON Schema. DO NOT return anything except "
            "the structured data.\n\nJson Schema:\n{{schema}}\n\nOnly respond with the JSON."
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

StructuredDataPlanInput = StructuredDataPlan | Mapping[str, Any]
StructuredDataMultiInput = Mapping[str, StructuredDataPlanInput] | Iterable[Tuple[str, StructuredDataPlanInput]]


def _ensure_json_schema(schema: JsonSchema | Mapping[str, Any]) -> JsonSchema:
    if isinstance(schema, JsonSchema):
        return schema
    return JsonSchema(**schema)


def _ensure_structured_data_plan(plan: StructuredDataPlanInput) -> StructuredDataPlan:
    if isinstance(plan, StructuredDataPlan):
        return plan
    mutable_plan: MutableMapping[str, Any] = dict(plan)
    if "schema" in mutable_plan and "schema_" not in mutable_plan:
        mutable_plan["schema_"] = mutable_plan.pop("schema")
    if "schema_" not in mutable_plan:
        raise ValueError("Structured data plan requires a 'schema' entry.")
    mutable_plan["schema_"] = _ensure_json_schema(mutable_plan["schema_"])
    return StructuredDataPlan(**mutable_plan)


def structured_data_plan(
    *,
    schema: JsonSchema | Mapping[str, Any],
    messages: Iterable[Mapping[str, str]] | None = None,
    enabled: bool = True,
    timeout_seconds: float | None = None,
    min_messages_threshold: float | None = None,
) -> AnalysisPlan:
    """
    Build an AnalysisPlan that captures structured data via a JSON Schema extraction.
    """

    resolved_messages = list(messages) if messages is not None else list(DEFAULT_STRUCTURED_DATA_MESSAGES)
    return AnalysisPlan(
        min_messages_threshold=min_messages_threshold,
        structured_data_plan=StructuredDataPlan(
            enabled=enabled,
            messages=resolved_messages,
            timeout_seconds=timeout_seconds,
            schema_=_ensure_json_schema(schema),
        ),
    )


def structured_data_multi_plan(
    plans: StructuredDataMultiInput,
    *,
    min_messages_threshold: float | None = None,
) -> AnalysisPlan:
    """
    Build an AnalysisPlan that runs multiple structured data extractions in one pass.
    """

    def _iter_entries() -> Iterator[Tuple[str, StructuredDataPlanInput]]:
        if isinstance(plans, Mapping):
            return iter(plans.items())
        return iter(plans)

    entries = [
        StructuredDataMultiPlan(
            key=key,
            plan=_ensure_structured_data_plan(plan),
        )
        for key, plan in _iter_entries()
    ]

    return AnalysisPlan(
        min_messages_threshold=min_messages_threshold,
        structured_data_multi_plan=entries,
    )
