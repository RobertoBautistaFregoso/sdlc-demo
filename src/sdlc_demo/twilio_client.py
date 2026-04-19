from __future__ import annotations

from typing import Any

from twilio.request_validator import RequestValidator
from twilio.rest import Client as TwilioRestClient

from sdlc_demo.config import Settings


def verify_signature(
    *,
    auth_token: str,
    url: str,
    params: dict[str, Any],
    signature: str | None,
) -> bool:
    if not signature:
        return False
    validator = RequestValidator(auth_token)
    return validator.validate(url, params, signature)


class TwilioClient:
    def __init__(self, settings: Settings, *, rest_client: TwilioRestClient | None = None) -> None:
        self._settings = settings
        self._rest = rest_client or TwilioRestClient(
            settings.twilio_account_sid, settings.twilio_auth_token
        )

    def send_message(
        self,
        *,
        to: str,
        body: str,
        button_text: str | None = None,
        button_payload: str | None = None,
    ) -> None:
        # Interactive WhatsApp buttons require registered content templates
        # (Twilio Content API). Until those templates are registered we send
        # body-only and rely on the copy instructing the parent to tap/type
        # the payload; inbound webhooks still receive ButtonPayload when a
        # registered template is tapped.
        _ = (button_text, button_payload)
        self._rest.messages.create(
            from_=self._settings.twilio_from_number,
            to=to,
            body=body,
        )
