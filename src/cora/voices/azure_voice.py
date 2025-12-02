from __future__ import annotations

from typing import Optional

from .voice_profile import VoiceProfile


class AzureVoice:
    def __init__(self, provider: str = "azure") -> None:
        self.provider = provider
        self.ximena = self._profile("es-ES-XimenaNeural")

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
