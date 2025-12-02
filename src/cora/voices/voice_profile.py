from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class VoiceProfile:
    """
    Small helper that knows how to express itself in the Vapi voice payload
    format.  Instances are immutable so they can be shared safely.
    """

    provider: str
    voice_id: str
    model: Optional[str] = None
    speed: Optional[float] = None

    def payload(
        self,
        *,
        model: Optional[str] = None,
        speed: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Return a dict ready to be JSON-encoded for the Vapi assistant payload.
        Optional overrides let callers tweak the model or speed at send time.
        """
        result: Dict[str, Any] = {
            "provider": self.provider,
            "voiceId": self.voice_id,
        }

        resolved_model = self.model if model is None else model
        resolved_speed = self.speed if speed is None else speed

        if resolved_model:
            result["model"] = resolved_model
        if resolved_speed is not None:
            result["speed"] = resolved_speed

        return result
