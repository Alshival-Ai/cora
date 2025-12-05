from __future__ import annotations

from typing import Mapping, Optional

from .voice_profile import VoiceProfile
from .utils import VoiceEntry, combine_voice_entries


DEFAULT_ELEVEN_VOICE_ENTRIES: list[VoiceEntry] = [
    ("payne", "wPZU8v1TgihzaR9aQ8Wj"),
    ("will", "bIHbv24MWmeRgasZH58o"),
    ("manav", "2BsEFcU7jUhLaUwV4h7l"),
    ("alon", "MZb4jD8N3GIedB0K3Xoi"),
    ("alex_ozwyn", "ZncGbt9ecxkwpmaX6V9z"),
    ("christina", "2qfp6zPuviqeCOZIE9RZ"),
    ("jennifer", "TcAStCk0faGcHdNIFX23"),
    ("jessica", "cgSgspJ2msm6clMCkdW9"),
    ("edward", "2BJW5coyhAzSr8STdHbE"),
    ("annabell", "02y4x5i9YrzYlFvGo1pp"),
    ("greg", "kfAgTu73p0UPH0WkLC53"),
    ("clyde", "2EiwWnXFnvU5JabPnv8n"),
    ("jake", "yDUXXKsu0jF5vdJnWAPU"),
    ("kim", "LLEUnU5vlkaEV6dSdkOl"),
    ("chelsea", "NHRgOEwqx5WZNClv5sat"),
    ("dakota", "P7x743VjyZEOihNNygQ9"),
    ("david", "v9LgF91V36LGgbLX3iHW"),
    ("gigi", "jBpfuIE2acCO8z3wKNLl"),
    ("nikky", "lTvtSobl0SaWDikyBCB6"),
    ("clara", "Qggl4b0xRMiqOwhPtVWT"),
    ("jacob_eder", "0c14Fsfhfnl8M9pCB5pf"),
    ("carlose", "fsl9wxwCbGk0XzqV61Fj"),
    ("emily", "LcfcDJNUP1GQjkzn1xUU"),
    ("roger", "CwhRBWXzGAHq8TQ4Fs17"),
    ("bill", "pqHfZKP75CvOlQylNhV4"),
    ("paola", "uCn98X6tKa49TnMFbwg6"),
    ("karen", "jqVMajy0TkayOvIB8eCz"),
    ("freya", "jsCqWAovK2LkecY7zXl4"),
    ("mark", "UgBBYS2sOqTuMpoF3BR0"),
    ("storytime", "iUqOXhMfiOIbBejNtfLR"),
    ("ana_maria", "m7yTemJqdIqrcNleANfX"),
]


class ElevenLabs:
    def __init__(
        self,
        voice_model: str = "eleven_multilingual_v2",
        *,
        additional_voices: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.provider = "11labs"
        self.voice_model = voice_model
        voice_entries = combine_voice_entries(
            DEFAULT_ELEVEN_VOICE_ENTRIES,
            additions=additional_voices,
        )
        for attribute, voice_id in voice_entries:
            setattr(self, attribute, self._profile(voice_id))

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
