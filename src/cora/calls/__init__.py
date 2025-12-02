from __future__ import annotations

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
    phone_number_id: str,
    customer: Customer,
    v: Optional[VapiConnector] = None,
) -> Any:
    """
    Create a Vapi call for the given assistant + phone number combination.
    Accepts customer as either a str (+1…) or {"number": "+1…"} dict.
    """
    payload = _normalize_customer(customer)
    client = v or VapiConnector()
    return client.calls.create(
        assistant_id=assistant_id,
        phone_number_id=phone_number_id,
        customer=payload,
    )


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
) -> Any:
    """
    Block until the call is terminal or the timeout expires. Optionally echo new
    messages for quick debugging. Returns the final call object as provided by
    Vapi's SDK.
    """
    deadline = time.time() + timeout_seconds
    seen_messages: set[str] = set()
    last_status: Optional[str] = None

    while True:
        call_obj = v.calls.get(call_id)
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
            return call_obj

        if time.time() > deadline:
            return call_obj

        time.sleep(interval)


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
