from __future__ import annotations

from typing import Optional

from .voice_profile import VoiceProfile


class ElevenLabs:
    def __init__(self, voice_model: str = "eleven_multilingual_v2") -> None:
        self.provider = "11labs"
        self.voice_model = voice_model
        self.jennifer = self._profile("TcAStCk0faGcHdNIFX23")
        self.christina = self._profile("2qfp6zPuviqeCOZIE9RZ")
        self.ana_maria = self._profile("m7yTemJqdIqrcNleANfX")

    def custom(
        self,
        voice_id: str,
        *,
        model: Optional[str] = None,
        speed: Optional[float] = None,
    ) -> VoiceProfile:
        """
        Convenience helper for voices not hard-coded above.
        """
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
