from __future__ import annotations

from typing import Any, Dict, Optional

from .transcriber_profile import TranscriberProfile


class Deepgram:
    def __init__(self, default_model: str = "nova-2") -> None:
        self.provider = "deepgram"
        self.default_model = default_model
        self.english = self._profile(language="en")
        self.spanish = self._profile(language="es")

    def custom(
        self,
        *,
        language: Optional[str] = None,
        lang: Optional[str] = None,
        model: Optional[str] = None,
        **options: Any,
    ) -> TranscriberProfile:
        """
        Build a profile for any Deepgram combination that is not already
        provided as a preset. Accepts both `language=` and `lang=` for parity
        with how callers may specify patient language.
        """
        language = language or lang
        return self._profile(language=language, model=model, options=options)

    def _profile(
        self,
        *,
        language: Optional[str],
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> TranscriberProfile:
        return TranscriberProfile(
            provider=self.provider,
            model=model or self.default_model,
            language=language,
            options=dict(options or {}),
        )
