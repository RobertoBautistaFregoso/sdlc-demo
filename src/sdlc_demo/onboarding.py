from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from enum import Enum

from dateutil import parser as du_parser

from sdlc_demo import copy


class OnboardingState(str, Enum):
    AWAITING_START = "awaiting_start"
    AWAITING_CONSENT = "awaiting_consent"
    AWAITING_NAME = "awaiting_name"
    AWAITING_DATE = "awaiting_date"
    DIAGNOSTIC_PENDING = "diagnostic_pending"


@dataclass(frozen=True)
class StudentProfile:
    whatsapp_number: str
    onboarding_state: OnboardingState = OnboardingState.AWAITING_START
    student_first_name: str | None = None
    exam_date: date | None = None
    consent_text: str | None = None
    consent_at: datetime | None = None


@dataclass(frozen=True)
class InboundMessage:
    whatsapp_number: str
    body: str = ""
    button_payload: str | None = None


@dataclass(frozen=True)
class OutboundMessage:
    body: str
    button_text: str | None = None
    button_payload: str | None = None


@dataclass(frozen=True)
class TransitionResult:
    profile: StudentProfile
    outbound: list[OutboundMessage] = field(default_factory=list)


_SPANISH_MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

_SPANISH_DATE_RE = re.compile(
    r"^(\d{1,2})\s+de\s+([a-záéíóú]+)(?:\s+de\s+(\d{4}))?$",
    re.IGNORECASE,
)


_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_exam_date(text: str, *, today: date | None = None) -> date | None:
    text = (text or "").strip().lower()
    if not text:
        return None

    if _ISO_DATE_RE.match(text):
        try:
            return date.fromisoformat(text)
        except ValueError:
            return None

    m = _SPANISH_DATE_RE.match(text)
    if m:
        day = int(m.group(1))
        month = _SPANISH_MONTHS.get(m.group(2))
        if month is None:
            return None
        year_str = m.group(3)
        year = int(year_str) if year_str else (today or date.today()).year
        try:
            return date(year, month, day)
        except ValueError:
            return None

    try:
        return du_parser.parse(text, dayfirst=True, fuzzy=False).date()
    except (ValueError, OverflowError):
        return None


def advance(
    profile: StudentProfile,
    inbound: InboundMessage,
    *,
    now: datetime | None = None,
) -> TransitionResult:
    now = now or datetime.now(tz=timezone.utc)
    state = profile.onboarding_state

    if state is OnboardingState.AWAITING_START:
        out = OutboundMessage(
            body=copy.WELCOME_BODY,
            button_text=copy.WELCOME_BUTTON,
            button_payload=copy.WELCOME_BUTTON_PAYLOAD,
        )
        return TransitionResult(
            profile=replace(profile, onboarding_state=OnboardingState.AWAITING_CONSENT),
            outbound=[out],
        )

    if state is OnboardingState.AWAITING_CONSENT:
        consent_prompt = OutboundMessage(
            body=copy.CONSENT_BODY,
            button_text=copy.CONSENT_BUTTON,
            button_payload=copy.CONSENT_BUTTON_PAYLOAD,
        )
        if inbound.button_payload == copy.WELCOME_BUTTON_PAYLOAD:
            return TransitionResult(profile=profile, outbound=[consent_prompt])
        if inbound.button_payload == copy.CONSENT_BUTTON_PAYLOAD:
            next_profile = replace(
                profile,
                onboarding_state=OnboardingState.AWAITING_NAME,
                consent_text=copy.CONSENT_RECORD_TEXT,
                consent_at=now,
            )
            return TransitionResult(
                profile=next_profile,
                outbound=[OutboundMessage(body=copy.ASK_NAME_BODY)],
            )
        return TransitionResult(profile=profile, outbound=[consent_prompt])

    if state is OnboardingState.AWAITING_NAME:
        name = (inbound.body or "").strip()
        if 0 < len(name) <= 60:
            next_profile = replace(
                profile,
                onboarding_state=OnboardingState.AWAITING_DATE,
                student_first_name=name,
            )
            return TransitionResult(
                profile=next_profile,
                outbound=[OutboundMessage(body=copy.ASK_DATE_BODY)],
            )
        return TransitionResult(
            profile=profile,
            outbound=[OutboundMessage(body=copy.ASK_NAME_BODY)],
        )

    if state is OnboardingState.AWAITING_DATE:
        parsed = parse_exam_date(inbound.body)
        if parsed is not None:
            next_profile = replace(
                profile,
                onboarding_state=OnboardingState.DIAGNOSTIC_PENDING,
                exam_date=parsed,
            )
            return TransitionResult(
                profile=next_profile,
                outbound=[OutboundMessage(body=copy.DONE_BODY)],
            )
        return TransitionResult(
            profile=profile,
            outbound=[OutboundMessage(body=copy.ASK_DATE_BODY)],
        )

    if state is OnboardingState.DIAGNOSTIC_PENDING:
        return TransitionResult(
            profile=profile,
            outbound=[OutboundMessage(body=copy.DIAGNOSTIC_PENDING_STUB_BODY)],
        )

    raise ValueError(f"unknown onboarding state: {state}")
