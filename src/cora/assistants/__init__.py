from __future__ import annotations

import os
import re
from typing import Any, Dict, Mapping, Optional, Sequence, Union

from ..analysis_plan import pass_fail_plan
from ..transcribers.transcriber_profile import TranscriberProfile
from ..vapi_client import VapiConnector
from ..voices.voice_profile import VoiceProfile

DEFAULT_MODEL_PROVIDER = os.getenv("VAPI_MODEL_PROVIDER", "openai")
DEFAULT_MODEL_NAME = os.getenv("VAPI_MODEL_NAME", "gpt-5.1")
DEFAULT_TOOL_IDS = [
    item.strip()
    for item in (os.getenv("VAPI_TOOL_IDS", "")).split(",")
    if item.strip()
]
DEFAULT_TOOLS = [{"type": "endCall"}]
UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

VoiceInput = Union[VoiceProfile, Mapping[str, Any]]
TranscriberInput = Union[TranscriberProfile, Mapping[str, Any]]


def create_assistant(
    *,
    name: str,
    system_prompt: str,
    tool_ids: Optional[Sequence[str]] = None,
    tools: Optional[Sequence[Mapping[str, Any]]] = None,
    voice: VoiceInput,
    transcriber: TranscriberInput,
    analysis_plan: Optional[Any] = None,
    background_speech_denoising_plan: Optional[Any] = None,
    first_message: Optional[str] = None,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    connector: Optional[VapiConnector] = None,
    model_overrides: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Thin wrapper around vapi.assistants.create that wires together the common
    defaults used across assistants in this project.
    """
    client = connector or VapiConnector()

    model_payload: Dict[str, Any] = {
        "provider": model_provider or DEFAULT_MODEL_PROVIDER,
        "model": model_name or DEFAULT_MODEL_NAME,
        "messages": [{"role": "system", "content": system_prompt}],
        "tools": list(tools or DEFAULT_TOOLS),
    }
    resolved_tool_ids = list(tool_ids) if tool_ids else list(DEFAULT_TOOL_IDS)
    if resolved_tool_ids:
        invalid_tool_ids = [tool_id for tool_id in resolved_tool_ids if not UUID_PATTERN.match(tool_id)]
        if invalid_tool_ids:
            raise ValueError(
                "tool_ids must be UUIDs. Remove or replace invalid values: "
                f"{invalid_tool_ids}. Check VAPI_TOOL_IDS or pass tool_ids explicitly."
            )
    if resolved_tool_ids:
        model_payload["toolIds"] = resolved_tool_ids
    if model_overrides:
        model_payload.update(model_overrides)

    assistant_voice = _voice_payload(voice)
    assistant_transcriber = _transcriber_payload(transcriber)
    plan = analysis_plan or pass_fail_plan()

    payload: Dict[str, Any] = {
        "name": name,
        "model": model_payload,
        "voice": assistant_voice,
        "first_message": first_message,
        "transcriber": assistant_transcriber,
        "analysis_plan": plan,
    }
    if background_speech_denoising_plan is not None:
        payload["background_speech_denoising_plan"] = background_speech_denoising_plan

    return client.assistants.create(
        **payload,
    )


def _voice_payload(voice: VoiceInput) -> Dict[str, Any]:
    if isinstance(voice, VoiceProfile):
        return voice.payload()
    return dict(voice)


def _transcriber_payload(transcriber: TranscriberInput) -> Dict[str, Any]:
    if isinstance(transcriber, TranscriberProfile):
        return transcriber.payload()
    return dict(transcriber)
