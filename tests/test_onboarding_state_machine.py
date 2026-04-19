from datetime import date, datetime, timezone

from sdlc_demo import copy
from sdlc_demo.onboarding import (
    InboundMessage,
    OnboardingState,
    StudentProfile,
    advance,
    parse_exam_date,
)

NUMBER = "+5215512345678"
FIXED_NOW = datetime(2026, 4, 18, 15, 0, tzinfo=timezone.utc)


def _profile(state: OnboardingState, **overrides) -> StudentProfile:
    return StudentProfile(whatsapp_number=NUMBER, onboarding_state=state, **overrides)


def _inbound(body: str = "", button_payload: str | None = None) -> InboundMessage:
    return InboundMessage(whatsapp_number=NUMBER, body=body, button_payload=button_payload)


def test_awaiting_start_any_message_sends_welcome_and_advances() -> None:
    result = advance(_profile(OnboardingState.AWAITING_START), _inbound(body="hola"), now=FIXED_NOW)

    assert result.profile.onboarding_state is OnboardingState.AWAITING_CONSENT
    assert len(result.outbound) == 1
    out = result.outbound[0]
    assert out.body == copy.WELCOME_BODY
    assert out.button_text == copy.WELCOME_BUTTON
    assert out.button_payload == copy.WELCOME_BUTTON_PAYLOAD


def test_awaiting_consent_empezar_button_sends_consent_prompt_no_advance() -> None:
    result = advance(
        _profile(OnboardingState.AWAITING_CONSENT),
        _inbound(button_payload=copy.WELCOME_BUTTON_PAYLOAD),
        now=FIXED_NOW,
    )

    assert result.profile.onboarding_state is OnboardingState.AWAITING_CONSENT
    assert result.profile.consent_text is None
    assert result.profile.consent_at is None
    assert len(result.outbound) == 1
    assert result.outbound[0].button_payload == copy.CONSENT_BUTTON_PAYLOAD
    assert result.outbound[0].body == copy.CONSENT_BODY


def test_awaiting_consent_acepto_button_records_consent_and_advances() -> None:
    result = advance(
        _profile(OnboardingState.AWAITING_CONSENT),
        _inbound(button_payload=copy.CONSENT_BUTTON_PAYLOAD),
        now=FIXED_NOW,
    )

    assert result.profile.onboarding_state is OnboardingState.AWAITING_NAME
    assert result.profile.consent_text == copy.CONSENT_RECORD_TEXT
    assert result.profile.consent_at == FIXED_NOW
    assert result.outbound == [type(result.outbound[0])(body=copy.ASK_NAME_BODY)]


def test_awaiting_consent_free_text_reprompts_and_does_not_record_consent() -> None:
    result = advance(
        _profile(OnboardingState.AWAITING_CONSENT),
        _inbound(body="sí claro"),
        now=FIXED_NOW,
    )

    assert result.profile.onboarding_state is OnboardingState.AWAITING_CONSENT
    assert result.profile.consent_text is None
    assert result.profile.consent_at is None
    assert len(result.outbound) == 1
    assert result.outbound[0].button_payload == copy.CONSENT_BUTTON_PAYLOAD


def test_awaiting_name_valid_text_stores_name_and_advances() -> None:
    result = advance(
        _profile(OnboardingState.AWAITING_NAME),
        _inbound(body="  Sofía  "),
        now=FIXED_NOW,
    )

    assert result.profile.onboarding_state is OnboardingState.AWAITING_DATE
    assert result.profile.student_first_name == "Sofía"
    assert result.outbound[0].body == copy.ASK_DATE_BODY


def test_awaiting_name_empty_reprompts() -> None:
    result = advance(
        _profile(OnboardingState.AWAITING_NAME),
        _inbound(body="   "),
        now=FIXED_NOW,
    )

    assert result.profile.onboarding_state is OnboardingState.AWAITING_NAME
    assert result.profile.student_first_name is None
    assert result.outbound[0].body == copy.ASK_NAME_BODY


def test_awaiting_date_iso_stores_date_and_advances() -> None:
    result = advance(
        _profile(OnboardingState.AWAITING_DATE, student_first_name="Sofía"),
        _inbound(body="2026-09-01"),
        now=FIXED_NOW,
    )

    assert result.profile.onboarding_state is OnboardingState.DIAGNOSTIC_PENDING
    assert result.profile.exam_date == date(2026, 9, 1)
    assert result.outbound[0].body == copy.DONE_BODY


def test_awaiting_date_spanish_month_is_parsed() -> None:
    result = advance(
        _profile(OnboardingState.AWAITING_DATE, student_first_name="Sofía"),
        _inbound(body="1 de septiembre de 2026"),
        now=FIXED_NOW,
    )

    assert result.profile.exam_date == date(2026, 9, 1)
    assert result.profile.onboarding_state is OnboardingState.DIAGNOSTIC_PENDING


def test_awaiting_date_ddmmyyyy_is_parsed() -> None:
    result = advance(
        _profile(OnboardingState.AWAITING_DATE, student_first_name="Sofía"),
        _inbound(body="01/09/2026"),
        now=FIXED_NOW,
    )

    assert result.profile.exam_date == date(2026, 9, 1)


def test_awaiting_date_unparseable_reprompts() -> None:
    result = advance(
        _profile(OnboardingState.AWAITING_DATE, student_first_name="Sofía"),
        _inbound(body="no sé"),
        now=FIXED_NOW,
    )

    assert result.profile.onboarding_state is OnboardingState.AWAITING_DATE
    assert result.profile.exam_date is None
    assert result.outbound[0].body == copy.ASK_DATE_BODY


def test_resume_from_awaiting_name_is_identical_to_cold_turn() -> None:
    seeded = _profile(
        OnboardingState.AWAITING_NAME,
        consent_text=copy.CONSENT_RECORD_TEXT,
        consent_at=FIXED_NOW,
    )
    result = advance(seeded, _inbound(body="Sofía"), now=FIXED_NOW)

    assert result.profile.onboarding_state is OnboardingState.AWAITING_DATE
    assert result.profile.student_first_name == "Sofía"
    assert result.profile.consent_text == copy.CONSENT_RECORD_TEXT
    assert result.profile.consent_at == FIXED_NOW


def test_diagnostic_pending_returns_stub_and_does_not_mutate() -> None:
    seeded = _profile(
        OnboardingState.DIAGNOSTIC_PENDING,
        student_first_name="Sofía",
        exam_date=date(2026, 9, 1),
        consent_text=copy.CONSENT_RECORD_TEXT,
        consent_at=FIXED_NOW,
    )
    result = advance(seeded, _inbound(body="hola de nuevo"), now=FIXED_NOW)

    assert result.profile == seeded
    assert result.outbound[0].body == copy.DIAGNOSTIC_PENDING_STUB_BODY


def test_parse_exam_date_rejects_garbage() -> None:
    assert parse_exam_date("no es una fecha") is None
    assert parse_exam_date("") is None
    assert parse_exam_date("32 de enero") is None
