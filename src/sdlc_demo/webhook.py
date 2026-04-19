from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from sdlc_demo.config import Settings, get_settings
from sdlc_demo.onboarding import (
    InboundMessage,
    OnboardingState,
    StudentProfile,
    advance,
)
from sdlc_demo.repo import InMemoryStudentRepo, StudentRepo, SupabaseStudentRepo
from sdlc_demo.twilio_client import TwilioClient, verify_signature

router = APIRouter()

_repo_singleton: StudentRepo | None = None
_twilio_singleton: TwilioClient | None = None


def get_repo(settings: Settings = Depends(get_settings)) -> StudentRepo:
    global _repo_singleton
    if _repo_singleton is None:
        if settings.supabase_url and settings.supabase_key:
            from supabase import create_client

            client = create_client(settings.supabase_url, settings.supabase_key)
            _repo_singleton = SupabaseStudentRepo(client)
        else:
            _repo_singleton = InMemoryStudentRepo()
    return _repo_singleton


def get_twilio_client(settings: Settings = Depends(get_settings)) -> TwilioClient:
    global _twilio_singleton
    if _twilio_singleton is None:
        _twilio_singleton = TwilioClient(settings)
    return _twilio_singleton


async def verify_twilio_signature(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    form = await request.form()
    params: dict[str, Any] = {k: v for k, v in form.items()}
    if settings.twilio_skip_signature_verification:
        return params
    signature = request.headers.get("X-Twilio-Signature")
    url = settings.webhook_base_url.rstrip("/") + "/webhook"
    if not verify_signature(
        auth_token=settings.twilio_auth_token,
        url=url,
        params=params,
        signature=signature,
    ):
        raise HTTPException(status_code=403, detail={"error": "invalid_signature"})
    return params


@router.post("/webhook")
def webhook(
    params: dict[str, Any] = Depends(verify_twilio_signature),
    repo: StudentRepo = Depends(get_repo),
    twilio: TwilioClient = Depends(get_twilio_client),
) -> dict[str, Any]:
    from_raw = str(params.get("From", "") or "")
    whatsapp_number = from_raw.removeprefix("whatsapp:").strip()
    if not whatsapp_number:
        return {}

    body = str(params.get("Body", "") or "")
    button_payload_raw = params.get("ButtonPayload")
    button_payload = str(button_payload_raw) if button_payload_raw else None

    profile = repo.get(whatsapp_number) or StudentProfile(
        whatsapp_number=whatsapp_number,
        onboarding_state=OnboardingState.AWAITING_START,
    )
    inbound = InboundMessage(
        whatsapp_number=whatsapp_number,
        body=body,
        button_payload=button_payload,
    )

    result = advance(profile, inbound)

    repo.upsert(result.profile)
    for msg in result.outbound:
        twilio.send_message(
            to=f"whatsapp:{whatsapp_number}",
            body=msg.body,
            button_text=msg.button_text,
            button_payload=msg.button_payload,
        )
    return {}
