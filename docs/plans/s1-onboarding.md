# S1 — Onboard a new student via WhatsApp — Implementation Plan

**Story:** [S1 / issue #1](https://github.com/RobertoBautistaFregoso/sdlc-demo/issues/1)
**Branch:** `feat/s1-onboarding`
**Status:** Draft — awaiting PM review before implementation
**Sources:** `docs/stories.md` §S1, `docs/prd.md` §4.1 + §5 Flow A, `docs/adr/0001-stack.md`, `docs/testing.md`

---

## 1. Scope

### In scope for this PR
- `POST /webhook` upgraded to: verify Twilio HMAC → parse inbound message → drive onboarding state machine → persist profile → send outbound via Twilio.
- Onboarding state machine covering all four S1 acceptance scenarios (fresh chat, explicit consent, resume-from-last-step, required fields collected).
- Persistence of student profile: `whatsapp_number`, `onboarding_state`, `student_first_name`, `exam_date`, `consent_text`, `consent_at`.
- Outbound Mexican Spanish copy centralized in one module; interactive-button replies where WhatsApp supports them.
- First SQL migration under `supabase/migrations/`.
- Unit tests for the state machine, HMAC verifier, and Spanish copy; one integration test that replays a full onboarding flow against a mocked Twilio and an in-memory repo.

### Explicitly out of scope (deferred — story/issue noted)
| Deferred | Why | Lands in |
|---|---|---|
| Past-date rejection and `/fecha` update command | S2 owns date validation; S1 only needs to parse + store | S2 / issue #2 |
| Late-joiner (<42 days) warning + cohort flag | Separate `[must]` story with its own acceptance criteria | S3 / issue #3 |
| Diagnostic kickoff after onboarding | Terminal state is `diagnostic_pending`; S4 picks up from there | S4 / issue #4 |
| Off-topic refusal / `/ayuda` / `/pausar` / unknown commands | Safety guardrail is its own story | S16 / issue #12 |
| Real Postgres in tests (per `docs/testing.md` §b) | Needs Docker Compose + a test-DB harness we don't have yet | Ops PR (separate) |
| Twilio message-template approval for production | Meta/Twilio account work, not code; v1 ships against the Twilio sandbox | Ops, pre-launch |

Acceptance-criteria coverage: **S1 scenarios 1–4 all fully covered** in this PR. Nothing from S1 itself is punted.

---

## 2. Files to create / modify

### New
| Path | Purpose |
|---|---|
| `src/sdlc_demo/config.py` | `pydantic-settings` `Settings` reading Twilio + Supabase + Anthropic env vars. |
| `src/sdlc_demo/copy.py` | All Mexican Spanish strings and message builders used by S1. |
| `src/sdlc_demo/twilio_client.py` | Thin wrapper: `verify_signature(request)` and `send_message(to, body, buttons=None)` using the Twilio SDK. |
| `src/sdlc_demo/repo.py` | `StudentRepo` Protocol + `InMemoryStudentRepo` (tests) + `SupabaseStudentRepo` (dev/prod). |
| `src/sdlc_demo/onboarding.py` | Pure-function state machine: `advance(profile, inbound) -> (next_profile, outbound_actions)`. No I/O. |
| `src/sdlc_demo/webhook.py` | FastAPI router with `/webhook`: verify → load/create profile → advance → persist → send. |
| `supabase/migrations/0001_students.sql` | DDL for the `students` table (see §3). |
| `tests/test_onboarding_state_machine.py` | State-machine transitions + resume. |
| `tests/test_twilio_signature.py` | Valid / missing / tampered HMAC. |
| `tests/test_copy.py` | Smoke: key Spanish tokens present. |
| `tests/test_webhook_integration.py` | End-to-end flow against mocked Twilio + in-memory repo. |

### Modified
| Path | Change |
|---|---|
| `src/sdlc_demo/main.py` | Mount the webhook router; drop the inline `/webhook` stub. |
| `pyproject.toml` | Add runtime deps: `twilio>=9`, `supabase>=2`, `pydantic-settings>=2`, `python-dateutil>=2.9`. Add dev deps: `respx>=0.21`, `freezegun>=1.5`. |
| `.env.example` | Add `TWILIO_ACCOUNT_SID`, `TWILIO_FROM_NUMBER`, `WEBHOOK_BASE_URL`. |
| `CLAUDE.md` | One-line note on `supabase/migrations/` and how to apply them in dev. |

---

## 3. Data model

```sql
-- supabase/migrations/0001_students.sql
create table students (
    whatsapp_number       text        primary key,
    onboarding_state      text        not null,
    student_first_name    text,
    exam_date             date,
    consent_text          text,
    consent_at            timestamptz,
    created_at            timestamptz not null default now(),
    updated_at            timestamptz not null default now()
);

create index students_updated_at_idx on students (updated_at);
```

Notes:
- `whatsapp_number` is the natural PK (ADR §Auth: "WhatsApp number is identity").
- `consent_text` stores the literal acknowledgment ("Acepto"); with `consent_at` and `whatsapp_number` this satisfies S1 scenario 2's "Acepto + timestamp + number are stored as the consent record".
- All profile fields nullable until their step completes; `onboarding_state` is always set.
- No `late_joiner` column yet — S3 adds it in `0002_late_joiner.sql`.
- No diagnostic/attempt/mastery tables yet — S4 owns those.

---

## 4. Webhook contract

### Request — Twilio POST `/webhook` (form-encoded)
Fields we parse:
- `From` — e.g. `whatsapp:+5215512345678`. Strip the `whatsapp:` prefix to get the canonical `whatsapp_number`.
- `Body` — free-text message content.
- `ButtonText` / `ButtonPayload` — populated when the parent taps an interactive button.
- `MessageSid`, `AccountSid` — logged for traceability, not used for routing.

Header `X-Twilio-Signature` is read by the HMAC dependency.

### Response
| Situation | Status | Body |
|---|---|---|
| Valid signature, request handled | `200` | `{}` |
| Valid signature, inbound is empty / unparseable | `200` | `{}` (log and drop — Twilio retries are fine) |
| Missing or invalid signature | `403` | `{"error": "invalid_signature"}` |

Success is signalled by outbound Twilio calls made during the request, not by the HTTP reply — Twilio/WhatsApp ignore the response body.

### Processing model
Synchronous: HMAC → load/create profile → state-machine step → persist → outbound Twilio call(s) → return. If we start pushing the Twilio 15s webhook timeout we move to a background worker; not needed for S1.

---

## 5. Onboarding state machine

State is persisted in `students.onboarding_state`. On every webhook, `webhook.py` loads the profile by `From` (creating it with `awaiting_start` if absent) and calls `advance()`.

| State | Entered when | Expected inbound | Action | On anything else |
|---|---|---|---|---|
| `awaiting_start` | Row just created | Any text (e.g. `"hola"`) | Send welcome + single `Empezar` button; advance to `awaiting_consent`. | Treat as expected (first turn is always the welcome). |
| `awaiting_consent` | Welcome sent | Button payload `EMPEZAR` → send consent prompt + `Acepto` button (stay in `awaiting_consent`). Button payload `ACEPTO` → store `consent_text="Acepto"` + `consent_at=now()`; send ask-name; advance to `awaiting_name`. | Re-send the current consent prompt; no state change, no consent record written. |
| `awaiting_name` | Consent recorded | Non-empty text, ≤ 60 chars | Store `student_first_name`; send ask-date; advance to `awaiting_date`. | Re-send ask-name. |
| `awaiting_date` | Name recorded | Parseable date (see §Date parsing below) | Store `exam_date`; send completion message; advance to `diagnostic_pending`. | Re-send ask-date. S2 will replace this with real past/format validation. |
| `diagnostic_pending` | Date recorded | (S4 owns real handling.) | S1 sends a stub acknowledgment ("ya te avisamos cuando tengamos tu diagnóstico listo"). | Same stub. |

### Resume behaviour (S1 scenario 3)
There is no explicit "resume" code path. Because state lives in Postgres and `advance()` is stateless over its inputs, a parent returning after any gap automatically continues from whatever `onboarding_state` was last persisted. The integration test covers this by reconstructing mid-flow state directly and sending one more webhook.

### Button-vs-text precedence
`ButtonPayload` is matched first. If absent, fall back to `Body` text. In `awaiting_consent` we only accept the explicit payloads `EMPEZAR` / `ACEPTO` (no text shortcut) to satisfy S1 scenario 2's "must tap Acepto".

### Date parsing (S1 stopgap)
Accept, via `python-dateutil`: ISO (`2026-09-01`), `DD/MM/YYYY`, `D de <mes>` in Spanish (`1 de septiembre`, current year assumed). Anything else → re-prompt. S2 replaces this with the validated formal parser + past-date error.

---

## 6. Twilio HMAC verification

- Use `twilio.request_validator.RequestValidator(auth_token).validate(url, params, signature)`.
- `url` = `settings.WEBHOOK_BASE_URL + "/webhook"` — in dev this is your ngrok/Render URL.
- `params` = the full form-encoded body (`await request.form()` as a dict).
- `signature` = `X-Twilio-Signature` header.
- Wire as a FastAPI `Depends(verify_twilio_signature)` on the `/webhook` route; returns `403` on missing/invalid.
- No replay/nonce protection in S1 — `docs/testing.md` §a flags it as "if implemented"; defer.
- Config flag `TWILIO_SKIP_SIGNATURE_VERIFICATION=true` to allow local `curl` testing; logged loudly at startup when enabled so it can't silently ship to prod.

Test cases: valid signature → 200; missing header → 403; tampered body → 403.

---

## 7. Test plan

### Unit
**`test_onboarding_state_machine.py`**
- `awaiting_start` + `"hola"` → welcome emitted, state advances to `awaiting_consent`.
- `awaiting_consent` + `ButtonPayload=EMPEZAR` → consent prompt emitted; no consent record yet; stays in `awaiting_consent`.
- `awaiting_consent` + `ButtonPayload=ACEPTO` → `consent_text`/`consent_at` stored; ask-name emitted; advances to `awaiting_name`.
- `awaiting_consent` + free-text `"sí claro"` → consent prompt re-sent; **no consent record written**; no state change (S1 scenario 2).
- `awaiting_name` + `"Sofía"` → name stored, ask-date emitted, advances to `awaiting_date`.
- `awaiting_date` + `"2026-09-01"` → date stored, completion message emitted, advances to `diagnostic_pending`.
- Resume: seed a profile in `awaiting_name` + send any text; behaves identically to a cold `awaiting_name` turn (proves statelessness).
- `diagnostic_pending` + any input → stub reply, profile unchanged.

**`test_twilio_signature.py`**
- Valid signature → 200.
- Missing `X-Twilio-Signature` header → 403.
- Signature computed against a different body → 403.

**`test_copy.py`**
- Welcome contains "Bienvenido" (or equivalent); consent prompt contains "Acepto"; no string contains obvious English leakage (sanity regex).

### Integration — `test_webhook_integration.py`
- `TestClient` with FastAPI dependency override: `StudentRepo` → `InMemoryStudentRepo`, `verify_twilio_signature` → always-true.
- `respx` mocks Twilio outbound (`POST /2010-04-01/Accounts/{sid}/Messages.json`).
- Replay five inbound webhooks in order:
  1. `Body="hola"` → asserts welcome message POSTed with `Empezar` button.
  2. `ButtonPayload="EMPEZAR"` → asserts consent prompt POSTed with `Acepto` button.
  3. `ButtonPayload="ACEPTO"` → asserts ask-name POSTed.
  4. `Body="Sofía"` → asserts ask-date POSTed.
  5. `Body="2026-09-01"` → asserts completion message POSTed.
- Final repo state assertions: exactly one row, `onboarding_state='diagnostic_pending'`, `student_first_name='Sofía'`, `exam_date=2026-09-01`, `consent_text='Acepto'`, `consent_at` set (use `freezegun` to make the timestamp deterministic).
- Every webhook returns 200 with `{}`.

No Docker, no live Twilio, no live Supabase for CI.

---

## 8. Open questions for PM

1. **State-sequence sanity check.** Your brief named `welcome → name → grade → confirm → done`, but S1 acceptance criteria + PRD §4.1 describe `welcome → consent → name → exam_date → done` (no "grade", no explicit "confirm" recap). Plan follows the story, not the brief — please confirm, and say whether you want a `confirm` recap turn before `done`.
2. **Date-format scope in S1.** My stopgap accepts ISO, `DD/MM/YYYY`, and `"D de <mes>"`. Do you want more (e.g., `"1 sep"`, `"septiembre 1"`) or less (ISO only, defer everything else to S2)?
3. **Interactive buttons vs. text-only replies.** WhatsApp interactive buttons require template approval for production; the Twilio sandbox allows them free-form. Ship v1 assuming sandbox-only (buttons everywhere, as planned), or send text-only ("responde ACEPTO") and treat button payloads as a bonus?
4. **Supabase project provisioning.** Do you already have a Supabase project for dev? If not, I'll add `scripts/bootstrap_supabase.md` walking through project creation + env-var population so a reviewer can run this end-to-end.
5. **Consent wording.** S1 + PRD gesture at consent but don't prescribe text. Proposed stopgap: "Acepto que mi hijo/a practique con un tutor con inteligencia artificial sin supervisión directa, y que se guarde esta conversación en WhatsApp." You / legal to finalize before launch — confirm you're OK with me using this placeholder in the PR.
6. **Dependency injection wiring.** FastAPI `Depends` vs. module-level singletons for the Twilio client and repo? I'd lean `Depends` for testability. Flagging in case you have a preference, since this is the first PR that introduces real external clients.

---

## Verification (once implemented)

Local:
```
source .venv/bin/activate
pip install -e ".[dev]"
pytest                      # all tests green, incl. the full-flow integration
uvicorn sdlc_demo.main:app --reload --port 8000
# in another shell, simulate Twilio:
curl -X POST http://localhost:8000/webhook \
  -d 'From=whatsapp:+5215512345678&Body=hola' \
  -H 'X-Twilio-Signature: ...'   # or set TWILIO_SKIP_SIGNATURE_VERIFICATION=true
```

Against a real Supabase + Twilio sandbox:
- Populate `.env` from `.env.example`.
- Apply `supabase/migrations/0001_students.sql` via the Supabase SQL editor.
- Point the Twilio sandbox webhook at the Render deploy URL / ngrok.
- Message the sandbox from your WhatsApp number; walk through the five turns; confirm the row in Supabase matches expectations.
