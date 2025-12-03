from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence, Union

from ..calls import normalize_phone
from ..vapi_client import VapiConnector

__all__ = [
    "create_chat",
    "chat",
]

CustomerInput = Union[str, Mapping[str, Any]]
ChatInput = Union[str, Sequence[Any]]


def create_chat(
    *,
    assistant_id: str,
    message: ChatInput,
    customer: Optional[CustomerInput] = None,
    phone_number_id: Optional[str] = None,
    session_id: Optional[str] = None,
    stream: bool = False,
    name: Optional[str] = None,
    previous_chat_id: Optional[str] = None,
    assistant_overrides: Optional[Mapping[str, Any]] = None,
    squad_id: Optional[str] = None,
    use_llm_generated_message_for_outbound: bool = False,
    v: Optional[VapiConnector] = None,
) -> Any:
    """
    Create (or continue) a Vapi chat conversation. When starting a new SMS
    thread provide both `customer` and `phone_number_id`. When continuing an
    existing thread use `session_id`. `previous_chat_id` can be supplied to
    provide prior context for the model regardless of transport choice.

    Provide a `message` payload describing what should be sent (either a raw
    string or a list of chat messages). By default the text is forwarded
    directly to the customer (no LLM processing). Pass
    `use_llm_generated_message_for_outbound=True` when you want the assistant
    to generate the outbound response from that input instead.
    """
    client = v or VapiConnector()

    if session_id and (phone_number_id or customer is not None):
        raise ValueError("session_id cannot be combined with phone_number_id/customer transport arguments.")

    transport: Optional[Dict[str, Any]] = None
    if session_id is None:
        if phone_number_id is None:
            raise ValueError("phone_number_id is required when creating a new chat.")
        if customer is None:
            raise ValueError("customer is required when creating a new chat.")
        transport = _build_transport(
            phone_number_id=phone_number_id,
            customer=customer,
            use_llm_generated_message_for_outbound=use_llm_generated_message_for_outbound,
        )

    if message is None:
        raise ValueError("message is required when creating a chat.")

    payload: Dict[str, Any] = {
        "assistant_id": assistant_id,
        "input": _normalize_input(message),
        "stream": stream,
    }

    if transport is not None:
        payload["transport"] = transport
    if name is not None:
        payload["name"] = name
    if session_id is not None:
        payload["session_id"] = session_id
    if previous_chat_id is not None:
        payload["previous_chat_id"] = previous_chat_id
    if assistant_overrides is not None:
        payload["assistant_overrides"] = dict(assistant_overrides)
    if squad_id is not None:
        payload["squad_id"] = squad_id

    return client.chats.create(**payload)


def chat(**kwargs: Any) -> Any:
    """
    Convenience alias so callers can do `cora.chat(...)`.
    """
    return create_chat(**kwargs)


def _build_transport(
    *,
    phone_number_id: str,
    customer: CustomerInput,
    use_llm_generated_message_for_outbound: bool,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "type": "twilio.sms",
        "conversationType": "chat",
        "phoneNumberId": phone_number_id,
        "customer": _normalize_customer(customer),
        "useLLMGeneratedMessageForOutbound": use_llm_generated_message_for_outbound,
    }
    return payload


def _normalize_customer(customer: CustomerInput) -> Dict[str, Any]:
    if isinstance(customer, str):
        return {"number": normalize_phone(customer)}
    if not isinstance(customer, Mapping):
        raise ValueError("Customer must be a string or mapping containing a phone number.")
    payload = dict(customer)
    number = payload.get("number")
    if not number:
        raise ValueError("Customer mapping must include a 'number' field.")
    payload["number"] = normalize_phone(number)
    return payload


def _normalize_input(chat_input: ChatInput) -> ChatInput:
    if isinstance(chat_input, str):
        return chat_input
    return list(chat_input)
