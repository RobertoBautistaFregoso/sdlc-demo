from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from sdlc_demo import copy
from sdlc_demo.config import Settings
from sdlc_demo.main import app
from sdlc_demo.onboarding import OnboardingState
from sdlc_demo.repo import InMemoryStudentRepo
from sdlc_demo.webhook import get_repo, get_settings, get_twilio_client

PARENT_NUMBER_RAW = "whatsapp:+5215512345678"
PARENT_NUMBER = "+5215512345678"
FROZEN_TS = "2026-04-18 15:00:00"


@dataclass
class SentMessage:
    to: str
    body: str
    button_text: str | None = None
    button_payload: str | None = None


@dataclass
class RecordingTwilio:
    sent: list[SentMessage] = field(default_factory=list)

    def send_message(
        self,
        *,
        to: str,
        body: str,
        button_text: str | None = None,
        button_payload: str | None = None,
    ) -> None:
        self.sent.append(SentMessage(to=to, body=body, button_text=button_text, button_payload=button_payload))


@pytest.fixture
def repo() -> InMemoryStudentRepo:
    return InMemoryStudentRepo()


@pytest.fixture
def twilio() -> RecordingTwilio:
    return RecordingTwilio()


@pytest.fixture
def client(repo: InMemoryStudentRepo, twilio: RecordingTwilio):
    app.dependency_overrides[get_settings] = lambda: Settings(twilio_skip_signature_verification=True)
    app.dependency_overrides[get_repo] = lambda: repo
    app.dependency_overrides[get_twilio_client] = lambda: twilio
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _post(client: TestClient, **form) -> None:
    response = client.post("/webhook", data={"From": PARENT_NUMBER_RAW, **form})
    assert response.status_code == 200
    assert response.json() == {}


@freeze_time(FROZEN_TS)
def test_full_onboarding_flow(
    client: TestClient,
    repo: InMemoryStudentRepo,
    twilio: RecordingTwilio,
) -> None:
    # Turn 1: "hola" → welcome
    _post(client, Body="hola")
    assert len(twilio.sent) == 1
    assert twilio.sent[-1].to == f"whatsapp:{PARENT_NUMBER}"
    assert twilio.sent[-1].body == copy.WELCOME_BODY
    assert twilio.sent[-1].button_payload == copy.WELCOME_BUTTON_PAYLOAD

    # Turn 2: tap Empezar → consent prompt
    _post(client, ButtonPayload=copy.WELCOME_BUTTON_PAYLOAD)
    assert len(twilio.sent) == 2
    assert twilio.sent[-1].body == copy.CONSENT_BODY
    assert twilio.sent[-1].button_payload == copy.CONSENT_BUTTON_PAYLOAD

    # Turn 3: tap Acepto → ask-name
    _post(client, ButtonPayload=copy.CONSENT_BUTTON_PAYLOAD)
    assert len(twilio.sent) == 3
    assert twilio.sent[-1].body == copy.ASK_NAME_BODY

    # Turn 4: send name → ask-date
    _post(client, Body="Sofía")
    assert len(twilio.sent) == 4
    assert twilio.sent[-1].body == copy.ASK_DATE_BODY

    # Turn 5: send date → completion
    _post(client, Body="2026-09-01")
    assert len(twilio.sent) == 5
    assert twilio.sent[-1].body == copy.DONE_BODY

    # Final repo state
    stored = repo.get(PARENT_NUMBER)
    assert stored is not None
    assert stored.onboarding_state is OnboardingState.DIAGNOSTIC_PENDING
    assert stored.student_first_name == "Sofía"
    assert stored.exam_date == date(2026, 9, 1)
    assert stored.consent_text == copy.CONSENT_RECORD_TEXT
    assert stored.consent_at == datetime(2026, 4, 18, 15, 0, tzinfo=timezone.utc)
