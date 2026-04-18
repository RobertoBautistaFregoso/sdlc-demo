# MVP Test Strategy

**Scope:** v1 per PRD v0.2.1 — WhatsApp-only math practice bot for 6th-graders preparing for one CDMX private *secundaria*.
**Principle:** test the things that have branching logic, the one path that proves the loop works end-to-end, and the LLM output (because that's the only non-deterministic component). Skip everything else for v1.

## (a) Unit tests — anything with branching logic

| Module | What to test |
|---|---|
| **Mastery function** (`% correct over last 5; mastered ≥80%`) | <5 attempts → "still learning"; exactly 5 attempts at 4/5 = mastered; 5 attempts at 3/5 = not mastered; sliding window correctness when 6th attempt arrives. |
| **Question selection** | Weighting is inverse to current mastery; mastered topics down-weighted but not excluded; cold-start (no diagnostic) returns deterministic seed set; never returns a question already answered today. |
| **Onboarding state machine** | Each step advances only when its required field is present; resume-from-last-step works after gap; consent acknowledgment is required before any other step persists. |
| **Late-joiner detection** | Date <42 days = warning + cohort flag; date ≥42 days = no warning, no flag; off-by-one at the 42-day boundary. |
| **Slash-command parsing** | `/progreso`, `/fecha`, `/pausar`, `/ayuda` recognized in any case/with leading whitespace; unknown commands route to the safety refusal (S16), not to the LLM. |
| **Twilio webhook auth** | Valid HMAC accepted; missing/invalid signature rejected with 403; replay protection if implemented. |
| **Cohort exclusion logic** | Late-joiner students excluded from primary-metric calculation; non-late-joiners included. |
| **Reference-answer grounding constraint** | The pre-LLM prompt builder always includes the reference answer; the post-LLM validator rejects explanations that name a different answer than the reference. |

Target: ~85% line coverage on these modules. No coverage target on glue code.

## (b) End-to-end happy-path test — note on surface

Playwright is a browser harness; **WhatsApp is not a browser**, so a literal Playwright test doesn't fit this MVP. The pragmatic equivalent is a **webhook-driven E2E test** that simulates Twilio's inbound webhooks and asserts on outbound calls + DB state.

**One happy-path test:**
1. POST a synthetic Twilio webhook representing parent's first "hola" → assert bot's outbound message is the welcome + consent prompt.
2. POST consent acknowledgment → assert state advances; bot asks for student name.
3. POST name + exam date (≥42 days out) → assert profile created in DB; bot starts diagnostic.
4. POST 25 diagnostic answers in sequence → assert per-topic mastery rows written; bot sends results message + image URL.
5. POST "Sí" to start practice → assert today's session generated with 10–15 questions weighted toward the lowest-mastery topics.
6. Assert `time_to_first_question_ms` was logged.

Mock the Twilio outbound API and the Anthropic API at the HTTP layer (use `respx` or `vcrpy`). Run against a real Postgres test database (Docker), not a mocked DB.

If a future debug/admin web UI is built (out of MVP), Playwright applies there. Not now.

## (c) Explicitly NOT tested in MVP

- **Visual regression.** One auto-rendered PNG (mastery bars). Not worth a screenshot harness; manual eyeball during dev is sufficient at v1 scale.
- **Load / performance testing.** v1 cohort target is ~50–200 students; we are nowhere near a load wall. Re-evaluate at v2.
- **Cross-device / cross-OS.** WhatsApp handles client rendering. We don't ship UI.
- **WhatsApp message-template approval flows.** Owned by Meta/Twilio; we test that templates are sent, not that Meta approves them.
- **Adversarial LLM red-teaming at scale.** Out of scope for v1; handled by manual audit (see d) and the off-topic-refusal guardrail (S16 unit-tested above).
- **Browser/Playwright tests of any kind** until there is a browser surface to test.
- **Mutation testing, fuzz testing, contract tests.** All v2+ if ever.

## (d) LLM-output testing — keep the explanation skill from regressing

Non-determinism + the explanation being the highest-stakes generated artifact (a wrong explanation harms a child preparing for a real exam) means we need a real eval, not a smoke test.

**Approach:**

1. **Fixture set.** ~30 hand-curated `(question, reference_answer, student_attempt)` triplets covering the math topics in scope. Stored in `tests/llm/fixtures/`. Grow as content authors add questions.
2. **Property-based assertions** per fixture (no exact-string matching — LLM output varies):
   - Explanation does **not** name a different answer than the reference (regex + small classifier).
   - Explanation **mentions or derives** the reference answer.
   - Output language detected as Spanish.
   - Reading-level score within the agreed grade rubric.
   - Length within bounds (e.g., 30–250 words).
   - No prompt-injection markers / no chain-of-thought leakage.
3. **Run trigger:** every PR that touches `prompts/`, the explanation pipeline, or the model version pin. Also nightly on `main`.
4. **Pass threshold:** ≥28/30 fixtures pass per run; failing PRs block merge. The 2-fixture slack accounts for LLM stochasticity even at low temperature.
5. **Determinism levers:** temperature ≤0.3 for the explanation call; prompt-cache the system prompt + per-question reference so the only varying input is the student attempt.
6. **Production audit.** Sample 20 random production explanations weekly during the v1 cohort; founder + (eventually) a math reviewer score them against the same property checks. Drift from the eval = signal to expand the fixture set.
7. **Model-version pinning.** Treat the LLM model ID as a versioned dependency. A model upgrade is a PR that must pass the eval before merging.

**What this catches:** prompt regressions, model-version regressions, reading-level drift, hallucinated alternative answers.
**What this misses:** subtle pedagogical quality (the production audit catches this) and edge cases not represented in the fixture set (grow the fixtures).
