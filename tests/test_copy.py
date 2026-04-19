import re

from sdlc_demo import copy

ALL_MESSAGES = [
    copy.WELCOME_BODY,
    copy.CONSENT_BODY,
    copy.ASK_NAME_BODY,
    copy.ASK_DATE_BODY,
    copy.DONE_BODY,
    copy.DIAGNOSTIC_PENDING_STUB_BODY,
]


def test_welcome_and_consent_contain_expected_spanish_tokens() -> None:
    assert "Bienvenido" in copy.WELCOME_BODY
    assert copy.WELCOME_BUTTON == "Empezar"
    assert "Acepto" in copy.CONSENT_BODY
    assert copy.CONSENT_BUTTON == "Acepto"
    assert copy.CONSENT_RECORD_TEXT == "Acepto"


def test_no_obvious_english_leakage() -> None:
    english_words = re.compile(
        r"\b(welcome|please|the|and|or|hello|yes|no|your|child|exam)\b",
        re.IGNORECASE,
    )
    for message in ALL_MESSAGES:
        assert not english_words.search(message), f"English leaked: {message!r}"
