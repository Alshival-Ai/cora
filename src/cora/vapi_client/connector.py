from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from vapi import Vapi
from dotenv import load_dotenv

DEFAULT_ENV_PATH = Path.cwd() / ".env"
API_KEY_ENV = "VAPI_API_KEY"
LEGACY_PRIVATE_KEY_ENV = "VAPI_PRIVATE_KEY"


class VapiConnector:
    """
    Centralized helper for creating a configured Vapi SDK client. It pulls
    credentials from (in priority order):
      1. Explicit token passed to the constructor
      2. OS environment variables (VAPI_PRIVATE_KEY / VAPI_API_KEY)
      3. The .env file at the project root (unless overridden)

    This keeps the assistants agnostic of how credentials are stored.
    """

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        env_path: Optional[Path | str] = None,
    ) -> None:
        env_file = Path(env_path) if env_path is not None else DEFAULT_ENV_PATH
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=False)
        else:
            load_dotenv(override=False)

        api_key = token or os.getenv(API_KEY_ENV)
        private_key = os.getenv(LEGACY_PRIVATE_KEY_ENV)

        if not private_key and not api_key:
            raise RuntimeError(
                f"Missing Vapi credentials. Provide {API_KEY_ENV} (or legacy {LEGACY_PRIVATE_KEY_ENV}) "
                "via argument, environment variable, or .env file."
            )

        self._client = self._init_client(private_key=private_key, api_key=api_key)

    @staticmethod
    def _init_client(
        *,
        private_key: Optional[str],
        api_key: Optional[str],
    ) -> Vapi:
        attempts = []
        if api_key:
            attempts.append(("api_key", api_key))
            attempts.append(("token", api_key))
        if private_key:
            attempts.append(("token", private_key))
            attempts.append(("api_key", private_key))

        for param, value in attempts:
            try:
                if param == "token":
                    return Vapi(token=value)
                return Vapi(api_key=value)
            except TypeError:
                continue

        fallback_value = api_key or private_key
        if fallback_value:
            prev_private = os.environ.get(LEGACY_PRIVATE_KEY_ENV)
            prev_api = os.environ.get(API_KEY_ENV)
            os.environ[LEGACY_PRIVATE_KEY_ENV] = fallback_value
            os.environ[API_KEY_ENV] = fallback_value
            try:
                return Vapi()
            finally:
                if prev_private is None:
                    os.environ.pop(LEGACY_PRIVATE_KEY_ENV, None)
                else:
                    os.environ[LEGACY_PRIVATE_KEY_ENV] = prev_private
                if prev_api is None:
                    os.environ.pop(API_KEY_ENV, None)
                else:
                    os.environ[API_KEY_ENV] = prev_api

        raise RuntimeError("Unable to initialize Vapi client with the provided credentials.")

    @property
    def assistants(self):
        return self._client.assistants

    @property
    def calls(self):
        return self._client.calls

    @property
    def chats(self):
        return self._client.chats

    @property
    def phone_numbers(self):
        return self._client.phone_numbers
