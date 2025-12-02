from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class TranscriberProfile:
    """
    Companion to VoiceProfile that makes it easy to emit Vapi-ready transcriber
    payloads while still allowing lightweight overrides when needed.
    """

    provider: str
    model: str
    language: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)

    def payload(
        self,
        *,
        model: Optional[str] = None,
        language: Optional[str] = None,
        **overrides: Any,
    ) -> Dict[str, Any]:
        """
        Produce the payload dict for Vapi.  Arbitrary keyword overrides can be
        supplied to tweak provider-specific flags (e.g., tier, keywords, etc.).
        """
        payload: Dict[str, Any] = {
            "provider": self.provider,
            "model": model or self.model,
        }

        resolved_language = self.language if language is None else language
        if resolved_language:
            payload["language"] = resolved_language

        payload.update(self.options)
        payload.update(overrides)
        return payload
