from fastapi.testclient import TestClient

from sdlc_demo.main import app

client = TestClient(app)


def test_webhook_post_returns_200() -> None:
    response = client.post("/webhook")
    assert response.status_code == 200
    assert response.json() == {}
