import pytest
from fastapi.testclient import TestClient
from twilio.request_validator import RequestValidator

from sdlc_demo.config import Settings
from sdlc_demo.main import app
from sdlc_demo.repo import InMemoryStudentRepo
from sdlc_demo.webhook import get_repo, get_settings, get_twilio_client

AUTH_TOKEN = "unit-test-auth-token"
BASE_URL = "http://testserver"
WEBHOOK_URL = f"{BASE_URL}/webhook"


class _FakeTwilio:
    def send_message(self, **_kwargs) -> None:
        pass


def _settings() -> Settings:
    return Settings(
        twilio_auth_token=AUTH_TOKEN,
        webhook_base_url=BASE_URL,
        twilio_skip_signature_verification=False,
    )


@pytest.fixture
def client():
    app.dependency_overrides[get_settings] = _settings
    app.dependency_overrides[get_repo] = lambda: InMemoryStudentRepo()
    app.dependency_overrides[get_twilio_client] = lambda: _FakeTwilio()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _sign(params: dict[str, str]) -> str:
    return RequestValidator(AUTH_TOKEN).compute_signature(WEBHOOK_URL, params)


def test_valid_signature_returns_200(client: TestClient) -> None:
    params = {"From": "whatsapp:+5215512345678", "Body": "hola"}
    signature = _sign(params)

    response = client.post("/webhook", data=params, headers={"X-Twilio-Signature": signature})

    assert response.status_code == 200
    assert response.json() == {}


def test_missing_signature_header_returns_403(client: TestClient) -> None:
    params = {"From": "whatsapp:+5215512345678", "Body": "hola"}

    response = client.post("/webhook", data=params)

    assert response.status_code == 403


def test_tampered_body_returns_403(client: TestClient) -> None:
    signed_params = {"From": "whatsapp:+5215512345678", "Body": "hola"}
    signature = _sign(signed_params)
    tampered = {"From": "whatsapp:+5215512345678", "Body": "not the signed body"}

    response = client.post("/webhook", data=tampered, headers={"X-Twilio-Signature": signature})

    assert response.status_code == 403
