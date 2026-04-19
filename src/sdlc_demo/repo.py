from __future__ import annotations

from datetime import date, datetime
from typing import Any, Protocol

from sdlc_demo.onboarding import OnboardingState, StudentProfile


class StudentRepo(Protocol):
    def get(self, whatsapp_number: str) -> StudentProfile | None: ...

    def upsert(self, profile: StudentProfile) -> None: ...


class InMemoryStudentRepo:
    def __init__(self) -> None:
        self._store: dict[str, StudentProfile] = {}

    def get(self, whatsapp_number: str) -> StudentProfile | None:
        return self._store.get(whatsapp_number)

    def upsert(self, profile: StudentProfile) -> None:
        self._store[profile.whatsapp_number] = profile


def _profile_to_row(profile: StudentProfile) -> dict[str, Any]:
    return {
        "whatsapp_number": profile.whatsapp_number,
        "onboarding_state": profile.onboarding_state.value,
        "student_first_name": profile.student_first_name,
        "exam_date": profile.exam_date.isoformat() if profile.exam_date else None,
        "consent_text": profile.consent_text,
        "consent_at": profile.consent_at.isoformat() if profile.consent_at else None,
    }


def _row_to_profile(row: dict[str, Any]) -> StudentProfile:
    exam_date_raw = row.get("exam_date")
    consent_at_raw = row.get("consent_at")
    return StudentProfile(
        whatsapp_number=row["whatsapp_number"],
        onboarding_state=OnboardingState(row["onboarding_state"]),
        student_first_name=row.get("student_first_name"),
        exam_date=date.fromisoformat(exam_date_raw) if exam_date_raw else None,
        consent_text=row.get("consent_text"),
        consent_at=datetime.fromisoformat(consent_at_raw) if consent_at_raw else None,
    )


class SupabaseStudentRepo:
    def __init__(self, client: Any) -> None:
        self._client = client

    def get(self, whatsapp_number: str) -> StudentProfile | None:
        resp = (
            self._client.table("students")
            .select("*")
            .eq("whatsapp_number", whatsapp_number)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            return None
        return _row_to_profile(rows[0])

    def upsert(self, profile: StudentProfile) -> None:
        self._client.table("students").upsert(_profile_to_row(profile)).execute()
