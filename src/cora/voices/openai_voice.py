from __future__ import annotations

from typing import Optional

from .voice_profile import VoiceProfile


class OpenAIVoice:
    def __init__(self, voice_model: str = "gpt-4o-mini-tts") -> None:
        self.provider = "openai"
        self.voice_model = voice_model
        self.nova = self._profile("nova")
        self.sage = self._profile("sage")

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
