from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict, Generator, Optional, Union

from ..vapi_client import VapiConnector

__all__ = [
    "TERMINAL_STATUSES",
    "normalize_phone",
    "create_call",
    "poll_until_terminal",
    "wait_for_terminal",
    "watch_call",
]

TERMINAL_STATUSES = {"ended", "failed", "noAnswer", "busy", "canceled"}
UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def _parse_phone_number_id(raw: Optional[str]) -> Optional[str]:
    if raw is None:
        return None
    trimmed = raw.strip()
    if not trimmed:
        return None
    trimmed = trimmed.split("#", 1)[0].strip()
    trimmed = trimmed.strip("\"'")
    return trimmed or None


DEFAULT_PHONE_NUMBER_ID = _parse_phone_number_id(os.getenv("VAPI_PHONE_NUMBER_ID"))


def normalize_phone(number: str) -> str:
    """
    Basic US-centric cleanup that approximates E.164 for +1 numbers.
    """
    digits = re.sub(r"\D+", "", number)
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    return number if number.startswith("+") else number


Customer = Union[str, Dict[str, str]]


def create_call(
    *,
    assistant_id: str,
    phone_number_id: Optional[str] = None,
    customer: Customer,
    assistant_overrides: Optional[Dict[str, Any]] = None,
    background_speech_denoising_plan: Optional[Any] = None,
    v: Optional[VapiConnector] = None,
) -> Any:
    """
    Create a Vapi call for the given assistant + phone number combination.
    Accepts customer as either a str (+1…) or {"number": "+1…"} dict.
    Use assistant_overrides/background_speech_denoising_plan to tweak
    assistant settings per call without changing the base assistant.
    """
    resolved_phone_number_id = _parse_phone_number_id(phone_number_id) or DEFAULT_PHONE_NUMBER_ID
    if not resolved_phone_number_id:
        raise ValueError(
            "phone_number_id is required; pass it explicitly or set VAPI_PHONE_NUMBER_ID in your environment."
        )
    if not UUID_PATTERN.match(resolved_phone_number_id):
        raise ValueError(
            "phone_number_id must be a UUID. Update VAPI_PHONE_NUMBER_ID or pass a UUID explicitly."
        )
    payload = _normalize_customer(customer)
    client = v or VapiConnector()
    call_payload: Dict[str, Any] = {
        "assistant_id": assistant_id,
        "phone_number_id": resolved_phone_number_id,
        "customer": payload,
    }
    overrides_payload: Optional[Dict[str, Any]] = None
    if assistant_overrides is not None:
        overrides_payload = dict(assistant_overrides)
    if background_speech_denoising_plan is not None:
        if overrides_payload is None:
            overrides_payload = {}
        overrides_payload["background_speech_denoising_plan"] = background_speech_denoising_plan
    if overrides_payload:
        call_payload["assistant_overrides"] = overrides_payload

    return client.calls.create(**call_payload)


def poll_until_terminal(
    v: VapiConnector,
    call_id: str,
    *,
    max_seconds: int = 600,
    interval: float = 2.5,
) -> Dict[str, Any]:
    """
    Poll the Vapi call endpoint until a terminal status is observed or the
    timeout expires. Returns a lightweight snapshot describing the final state.
    """
    deadline = time.time() + max_seconds
    last_message: Any = None
    status: Optional[str] = None
    call_obj: Any = None

    while time.time() < deadline:
        call_obj = v.calls.get(call_id)
        status = getattr(call_obj, "status", None)
        messages = getattr(call_obj, "messages", None) or []
        if messages:
            last_message = messages[-1]
        if _is_terminal(call_obj, status=status):
            break
        time.sleep(interval)

    return {
        "status": status or "unknown",
        "id": getattr(call_obj, "id", call_id) if call_obj is not None else call_id,
        "endedAt": getattr(call_obj, "endedAt", None) if call_obj is not None else None,
        "endedReason": getattr(call_obj, "endedReason", None) if call_obj is not None else None,
        "last_message": last_message,
    }


def wait_for_terminal(
    v: VapiConnector,
    call_id: str,
    *,
    timeout_seconds: int = 600,
    interval: float = 2.5,
    echo_messages: bool = True,
    pandas: bool = False,
) -> Any:
    """
    Block until the call is terminal or the timeout expires. Optionally echo new
    messages for quick debugging. Returns the final call object as provided by
    Vapi's SDK, or a pandas DataFrame row with the call payload when
    ``pandas=True``.
    """
    deadline = time.time() + timeout_seconds
    seen_messages: set[str] = set()
    last_status: Optional[str] = None
    final_call: Any = None

    while True:
        call_obj = v.calls.get(call_id)
        final_call = call_obj
        status = getattr(call_obj, "status", None)
        if status != last_status:
            last_status = status

        messages = getattr(call_obj, "messages", None) or []
        if echo_messages and messages:
            latest = messages[-1]
            key = str(latest)
            if key not in seen_messages:
                print(latest)
                seen_messages.add(key)

        if _is_terminal(call_obj, status=status):
            break

        if time.time() > deadline:
            break

        time.sleep(interval)

    if pandas:
        return _call_to_dataframe(final_call)
    return final_call


def watch_call(
    v: VapiConnector,
    call_id: str,
    *,
    interval: float = 2.5,
) -> Generator[Dict[str, Any], None, None]:
    """
    Generator that yields rolling snapshots {"id", "status", "last_message"}
    until a terminal state is reached.
    """
    seen_msg: Optional[str] = None
    while True:
        call_obj = v.calls.get(call_id)
        status = getattr(call_obj, "status", None)
        messages = getattr(call_obj, "messages", None) or []
        last_message = messages[-1] if messages else None
        payload = {
            "id": getattr(call_obj, "id", None),
            "status": status,
            "last_message": None,
        }
        if last_message is not None:
            last_key = str(last_message)
            if last_key != seen_msg:
                payload["last_message"] = last_message
                seen_msg = last_key
        yield payload
        if _is_terminal(call_obj, status=status):
            break
        time.sleep(interval)


def _normalize_customer(customer: Customer) -> Dict[str, str]:
    if isinstance(customer, str):
        return {"number": normalize_phone(customer)}
    if "number" in customer:
        return {"number": normalize_phone(customer["number"])}
    raise ValueError("Customer dict must contain a 'number' key.")


def _is_terminal(call_obj: Any, *, status: Optional[str]) -> bool:
    if status in TERMINAL_STATUSES:
        return True
    if call_obj is None:
        return False
    if getattr(call_obj, "endedAt", None) is not None:
        return True
    if getattr(call_obj, "endedReason", None) is not None:
        return True
    return False


def _call_to_dataframe(call_obj: Any):
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("pandas is required when `pandas=True` is passed to wait_for_terminal().") from exc

    payload = _call_to_payload(call_obj)
    if not payload:
        return pd.DataFrame([{}])
    return pd.DataFrame([payload])


def _call_to_payload(call_obj: Any) -> Dict[str, Any]:
    if call_obj is None:
        return {}

    analysis = getattr(call_obj, "analysis", None)
    messages = getattr(call_obj, "messages", None) or []

    customer = _safe_attr(call_obj, "customer", "customer_number", "customerNumber")
    customer_number = None
    if isinstance(customer, dict):
        customer_number = customer.get("number") or customer.get("phoneNumber")
    elif customer is not None:
        customer_number = customer

    payload: Dict[str, Any] = {
        "call_id": _safe_attr(call_obj, "id", "call_id"),
        "status": _safe_attr(call_obj, "status"),
        "assistant_id": _safe_attr(call_obj, "assistant_id", "assistantId"),
        "phone_number_id": _safe_attr(call_obj, "phone_number_id", "phoneNumberId"),
        "customer_number": customer_number,
        "created_at": _safe_attr(call_obj, "created_at", "createdAt"),
        "updated_at": _safe_attr(call_obj, "updated_at", "updatedAt"),
        "started_at": _safe_attr(call_obj, "started_at", "startedAt"),
        "ended_at": _safe_attr(call_obj, "ended_at", "endedAt"),
        "ended_reason": _safe_attr(call_obj, "ended_reason", "endedReason"),
        "cost": _safe_attr(call_obj, "cost"),
        "transcript": _safe_attr(call_obj, "transcript"),
        "messages": _serialize_messages(messages),
        "first_message": _safe_attr(call_obj, "first_message", "firstMessage"),
        "metadata": _object_to_python(_safe_attr(call_obj, "metadata")),
        "analysis_summary": _safe_attr(analysis, "summary"),
        "analysis_success_evaluation": _object_to_python(
            _safe_attr(analysis, "success_evaluation", "successEvaluation")
        ),
        "analysis_structured_data": _object_to_python(
            _safe_attr(analysis, "structured_data", "structuredData")
        ),
        "analysis_structured_data_multi": _object_to_python(
            _safe_attr(analysis, "structured_data_multi", "structuredDataMulti")
        ),
        "analysis_outcomes": _object_to_python(_safe_attr(analysis, "outcomes")),
    }

    return payload


def _safe_attr(obj: Any, *names: str) -> Any:
    if obj is None:
        return None
    for name in names:
        if name is None:
            continue
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return None


def _serialize_messages(messages: Any) -> Optional[str]:
    if not messages:
        return None

    serialized = []
    for message in messages:
        if hasattr(message, "json"):
            try:
                serialized.append(message.json())
                continue
            except TypeError:
                pass
        serialized.append(_object_to_python(message))
    try:
        return json.dumps(serialized, default=str)
    except TypeError:
        return str(serialized)


def _object_to_python(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {k: _object_to_python(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_object_to_python(v) for v in value]
    for attr in ("model_dump", "dict"):
        if hasattr(value, attr):
            method = getattr(value, attr)
            try:
                data = method()
            except TypeError:
                continue
            return _object_to_python(data)
    if hasattr(value, "__dict__"):
        return {
            k: _object_to_python(v)
            for k, v in value.__dict__.items()
            if not k.startswith("_") and not callable(v)
        }
    if hasattr(value, "json"):
        try:
            data = value.json()
        except TypeError:
            return str(value)
        if isinstance(data, str):
            return data
        return _object_to_python(data)
    return str(value)
