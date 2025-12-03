"""
Top-level package entrypoint for the Cora helper library.
"""

from .analysis_plan import pass_fail_plan
from .assistants import create_assistant
from .calls import (
    TERMINAL_STATUSES,
    create_call,
    normalize_phone,
    poll_until_terminal,
    wait_for_terminal,
    watch_call,
)
from .chats import chat, create_chat
from .phone_numbers import get_phone_number, list_phone_numbers
from .transcribers import deepgram_transcribers, Deepgram
from .voices import eleven_labs_voices, openai_voices, azure_voices
from .vapi_client import VapiConnector

__all__ = [
    "pass_fail_plan",
    "create_assistant",
    "TERMINAL_STATUSES",
    "create_call",
    "normalize_phone",
    "poll_until_terminal",
    "wait_for_terminal",
    "watch_call",
    "create_chat",
    "chat",
    "deepgram_transcribers",
    "Deepgram",
    "eleven_labs_voices",
    "openai_voices",
    "azure_voices",
    "VapiConnector",
    "list_phone_numbers",
    "get_phone_number",
]
