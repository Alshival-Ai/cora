from __future__ import annotations

from typing import Any, Dict, Optional

from .vapi_client import VapiConnector

__all__ = ["list_phone_numbers", "get_phone_number"]


def list_phone_numbers(
    *,
    connector: Optional[VapiConnector] = None,
    **filters: Any,
) -> Any:
    """
    Return all phone numbers visible to the authenticated Vapi account.
    Optional keyword arguments are forwarded to the underlying SDK call.
    """
    client = connector or VapiConnector()
    return client.phone_numbers.list(**filters)


def get_phone_number(
    phone_number_id: str,
    *,
    connector: Optional[VapiConnector] = None,
) -> Any:
    """
    Fetch a single phone number by ID (UUID) using the Vapi SDK.
    """
    client = connector or VapiConnector()
    return client.phone_numbers.get(phone_number_id)
