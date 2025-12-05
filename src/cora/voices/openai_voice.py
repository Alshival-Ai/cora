from __future__ import annotations

from typing import Mapping, Optional

from .voice_profile import VoiceProfile
from .utils import merge_voice_maps


DEFAULT_OPENAI_VOICES = {
    "fable": "fable",
    "verse": "verse",
    "sage": "sage",
    "onyx": "onyx",
    "marin": "marin",
    "cedar": "cedar",
    "ballad": "ballad",
    "shimmer": "shimmer",
    "coral": "coral",
    "ash": "ash",
    "nova": "nova",
    "echo": "echo",
    "alloy": "alloy",
}


class OpenAIVoice:
    def __init__(
        self,
        voice_model: str = "gpt-4o-mini-tts",
        *,
        additional_voices: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.provider = "openai"
        self.voice_model = voice_model
        voice_map = merge_voice_maps(
            defaults=DEFAULT_OPENAI_VOICES,
            additions=additional_voices,
        )
        for name, voice_id in voice_map.items():
            if hasattr(self, name):
                continue
            setattr(self, name, self._profile(voice_id))

    def custom(
        self,
        voice_id: str,
        *,
        model: Optional[str] = None,
        speed: Optional[float] = None,
    ) -> VoiceProfile:
        return self._profile(voice_id, model=model, speed=speed)

    def _profile(
        self,
        voice_id: str,
        *,
        model: Optional[str] = None,
        speed: Optional[float] = None,
    ) -> VoiceProfile:
        return VoiceProfile(
            provider=self.provider,
            voice_id=voice_id,
            model=model or self.voice_model,
            speed=speed,
        )
