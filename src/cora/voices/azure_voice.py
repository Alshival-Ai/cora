from __future__ import annotations

from typing import Mapping, Optional

from .voice_profile import VoiceProfile
from .utils import merge_voice_maps


DEFAULT_AZURE_VOICES = {
    "ximena": "es-ES-XimenaNeural",
}


class AzureVoice:
    def __init__(
        self,
        provider: str = "azure",
        *,
        additional_voices: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.provider = provider
        voice_map = merge_voice_maps(
            defaults=DEFAULT_AZURE_VOICES,
            additions=additional_voices,
        )
        for name, voice_id in voice_map.items():
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
            model=model,
            speed=speed,
        )
