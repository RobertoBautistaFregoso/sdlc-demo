# MVP User Stories

Source: `docs/prd.md` §4 (MVP scope) and §5 (key user flows).

**Tags:** `[must]` blocks MVP launch · `[should]` MVP needs it to be useful · `[nice]` defer if time-pressed.

**INVEST applied:** each story is independently shippable, negotiable, user-valuable, estimable in <1 sprint, small, and testable. Where two stories are tightly coupled (e.g., feedback + explanation), they are split anyway so engineering can sequence and ship them separately.

**Personas:** *Student* = 6th-grade student, ages 11–12. *Parent* = parent/guardian, non-paying enabler.

---

## Account & onboarding

- [ ] **S1 [must] — Create child account.** As a **parent**, I want to create an account for my child, so that they can start using the app for exam prep.
  - Account requires only what's needed (no PII beyond minimum); parent provides consent.
  - Student can log in on subsequent sessions without parent re-involvement.

  **Acceptance criteria**
  - **Scenario:** Parent creates an account for their child
    - **Given** I am a parent on the sign-up screen
    - **And** I have not previously created an account
    - **When** I submit the sign-up form with my email, my child's first name, and acknowledge the consent notice
    - **Then** an account is created and my child is signed in to the onboarding flow
  - **Scenario:** Student returns on a later session without parent
    - **Given** an account already exists for my child
    - **When** my child opens the app and signs in with the saved credentials
    - **Then** they reach the home screen without any parent re-authentication step
  - **Scenario:** Consent is required
    - **Given** I am on the sign-up form
    - **When** I attempt to submit without acknowledging the consent notice
    - **Then** the form is rejected with an inline message explaining consent is required

- [ ] **S2 [must] — Pick target exam.** As a **student**, I want to select my target *secundaria* entrance exam from a list, so that practice is calibrated to the right test.
  - List reflects exam(s) decided in PRD assumption A.
  - Selection is changeable later (with a reset of the diagnostic).

  **Acceptance criteria**
  - **Scenario:** First-time student picks a target exam
    - **Given** I have just signed in for the first time
    - **And** the curated list of supported exams is non-empty
    - **When** I select an exam from the list and confirm
    - **Then** the chosen exam is saved on my profile and I advance to the exam-date step
  - **Scenario:** Student changes their target exam later
    - **Given** I have already selected a target exam and completed a diagnostic
    - **When** I change my target exam from settings and confirm the change
    - **Then** my prior diagnostic results are cleared and I am prompted to take the diagnostic for the new exam
  - **Scenario:** No exam is selected
    - **Given** I am on the exam-selection step
    - **When** I attempt to proceed without selecting an exam
    - **Then** I cannot advance, and the list is highlighted with a "select an exam" message

- [ ] **S3 [must] — Set exam date.** As a **student**, I want to enter my exam date, so that the app can pace my preparation.
  - Date is editable later.
  - System uses date to compute time-to-exam shown in the dashboard.

  **Acceptance criteria**
  - **Scenario:** Student sets a future exam date during onboarding
    - **Given** I have selected a target exam
    - **When** I pick a date that is at least 1 day in the future and confirm
    - **Then** the date is saved on my profile and I advance to the diagnostic
  - **Scenario:** Student changes their exam date later
    - **Given** I have already set an exam date
    - **When** I change the date in settings and confirm
    - **Then** the new date is saved and the time-to-exam shown on my dashboard updates
  - **Scenario:** Invalid date rejected
    - **Given** I am on the exam-date step
    - **When** I attempt to confirm a date that is in the past
    - **Then** the form is rejected with an inline message and I cannot advance

## Initial diagnostic

- [ ] **S4 [must] — Take initial diagnostic.** As a **student**, I want to take a one-time diagnostic of ~20–30 questions, so that the app knows where I stand before practice begins.
  - Covers all in-scope topics for the chosen exam's MVP subject.
  - Produces a per-topic mastery estimate stored on my account.

  **Acceptance criteria**
  - **Scenario:** Student completes the diagnostic
    - **Given** I have selected a target exam and exam date
    - **And** I have not previously completed a diagnostic for this exam
    - **When** I answer all diagnostic questions and submit the final answer
    - **Then** a per-topic mastery estimate is computed and stored on my profile
    - **And** I am taken to the diagnostic results summary
  - **Scenario:** Diagnostic covers every in-scope topic
    - **Given** the diagnostic for my target exam has been generated
    - **When** I inspect the question set
    - **Then** every in-scope topic for the MVP subject is represented by at least one question
  - **Scenario:** Diagnostic length is bounded
    - **Given** I am taking the diagnostic
    - **When** I view the total question count
    - **Then** the count is between 20 and 30 inclusive
  - **Scenario:** Diagnostic is one-time per exam
    - **Given** I have completed the diagnostic for my current target exam
    - **When** I return to the home screen
    - **Then** I am not prompted to take the diagnostic again unless I change my target exam

- [ ] **S5 [should] — Pause and resume diagnostic.** As a **student**, I want to pause the diagnostic and pick it up later, so that I can complete it across multiple sittings without losing my place.
  - Progress persists across logout / app close.

- [ ] **S6 [must] — See diagnostic results summary.** As a **student**, I want a clear summary of my diagnostic results, so that I understand my starting point before I start practicing.
  - Per-topic mastery shown.
  - Includes a one-line framing of what to focus on first.

  **Acceptance criteria**
  - **Scenario:** Student sees results immediately after diagnostic
    - **Given** I have just completed the diagnostic
    - **When** I submit the final answer
    - **Then** the results summary is shown without requiring any further navigation
  - **Scenario:** Per-topic mastery is visible
    - **Given** I am viewing the results summary
    - **When** I scan the page
    - **Then** every in-scope topic is shown with its current mastery value
  - **Scenario:** "What to focus on first" is surfaced
    - **Given** I am viewing the results summary
    - **When** I look at the page
    - **Then** I see a single-sentence recommendation naming the topic to start with
  - **Scenario:** Student can begin practicing from the results screen
    - **Given** I am viewing the results summary
    - **When** I tap "Start practicing"
    - **Then** I begin today's first personalized practice session

## Practice loop

- [ ] **S7 [must] — Daily personalized session.** As a **student**, I want a "today's session" of 10–15 questions weighted toward my weakest topics, so that I spend my time on what matters most.
  - Selection algorithm uses current per-topic mastery (specific algorithm TBD per PRD review).
  - Session estimated at 15–20 min and can be completed in one sitting.

  **Acceptance criteria**
  - **Scenario:** Session generated on student return
    - **Given** I have completed the diagnostic
    - **And** I have not yet completed today's session
    - **When** I open the home screen
    - **Then** I see a "today's session" card with question count and estimated duration
  - **Scenario:** Session length is bounded
    - **Given** today's session has been generated for me
    - **When** I view the question set
    - **Then** the count is between 10 and 15 inclusive
  - **Scenario:** Weakest topics are prioritized
    - **Given** today's session has been generated
    - **And** my topics are ranked by current mastery
    - **When** I inspect the topic distribution of the session
    - **Then** my weakest topics are represented more frequently than my strongest topics
  - **Scenario:** Session is one-per-day
    - **Given** I have already completed today's session
    - **When** I return to the home screen later the same day
    - **Then** I am told today's session is done and shown when the next one will be available

- [ ] **S8 [must] — Immediate correct/incorrect feedback.** As a **student**, I want to see whether I got each question right or wrong immediately after I answer, so that I know how I'm doing without waiting.
  - Feedback shown after submit, before the next question.

  **Acceptance criteria**
  - **Scenario:** Correct answer
    - **Given** I am answering a practice question
    - **When** I submit the correct answer
    - **Then** I see a "correct" indicator before the next question is shown
  - **Scenario:** Incorrect answer
    - **Given** I am answering a practice question
    - **When** I submit an incorrect answer
    - **Then** I see an "incorrect" indicator before the next question is shown
    - **And** the correct answer is identified on screen
  - **Scenario:** Cannot skip past feedback
    - **Given** I have just submitted an answer
    - **When** I attempt to advance
    - **Then** I cannot move to the next question until the feedback view has been shown

- [ ] **S9 [must] — Plain-language explanation of the right answer.** As a **student**, I want a plain-language explanation of the correct answer to each question, so that I can learn from mistakes without needing an adult nearby.
  - Explanation generated against a known-correct reference answer (not free-form generation).
  - Reading level appropriate for a 6th-grade student in Mexico (specific level TBD per PRD review).

  **Acceptance criteria**
  - **Scenario:** Explanation accompanies feedback
    - **Given** I have just submitted an answer to a practice question
    - **When** the feedback view is shown
    - **Then** a plain-language explanation of the correct answer is visible alongside the correct/incorrect indicator
  - **Scenario:** Explanation is grounded in the reference answer
    - **Given** an explanation has been generated for a question
    - **When** the explanation is reviewed against the question's stored reference answer
    - **Then** the explanation defends the reference answer (it does not propose a different answer)
  - **Scenario:** Reading-level guardrail
    - **Given** an explanation has been generated
    - **When** measured with the agreed reading-level rubric (TBD per PRD)
    - **Then** the explanation meets the agreed grade-level target
  - **Scenario:** Explanation availability
    - **Given** I have answered a question (correctly or incorrectly)
    - **When** I view the feedback
    - **Then** an explanation is shown in 100% of cases (no silent fallback to "no explanation available")

- [ ] **S10 [nice] — Ask a follow-up "why".** As a **student**, I want to ask one bounded follow-up question on an explanation, so that I can clarify a point I didn't understand.
  - Follow-up is constrained to the current question's content (no open chat).
  - Safety: no PII collection; off-topic prompts are refused gracefully.

- [ ] **S11 [should] — See what changed at end of session.** As a **student**, I want to see how my mastery changed at the end of each session, so that I feel my effort produced real progress.
  - Shows per-topic deltas vs. start of session.
  - Surfaces the next recommended topic.

## Mastery dashboard

- [ ] **S12 [must] — Per-topic mastery view.** As a **student**, I want to see a per-topic mastery view, so that I can see where I'm strong and where I need work.
  - One bar per in-scope topic.
  - Definition of "mastery" is the same one used by the metric (TBD per PRD review).

  **Acceptance criteria**
  - **Scenario:** Dashboard shows one bar per in-scope topic
    - **Given** I have completed the diagnostic
    - **When** I open the mastery dashboard
    - **Then** I see exactly one mastery bar per in-scope topic for my target exam
  - **Scenario:** Mastery values reflect latest data
    - **Given** I have just completed a practice session that updated my mastery for some topics
    - **When** I open the mastery dashboard immediately after
    - **Then** the affected topic bars reflect the post-session values
  - **Scenario:** Definition is consistent with the metric
    - **Given** the agreed mastery function is defined (TBD per PRD)
    - **When** a topic bar is rendered
    - **Then** its value is computed by that same function (no separate display-only formula)
  - **Scenario:** Pre-diagnostic state
    - **Given** I have not yet completed the diagnostic
    - **When** I open the mastery dashboard
    - **Then** I see a prompt to take the diagnostic instead of empty bars

- [ ] **S13 [should] — "What to work on next" surface.** As a **student**, I want a clear "what to work on next" recommendation on the dashboard, so that I don't have to decide every day.
  - Single primary recommendation, not a list.

## Parent visibility

- [ ] **S14 [must] — Weekly parent summary.** As a **parent**, I want a weekly summary of my child's practice, so that I can tell whether the app is working without needing to understand the subject myself.
  - Delivered via the channel decided in PRD (email vs. in-app — currently undecided).
  - Includes sessions completed, topics practiced, and a simple progress signal.

  **Acceptance criteria**
  - **Scenario:** Summary delivered weekly
    - **Given** my child has had at least one practice session in the past 7 days
    - **When** the weekly delivery time is reached
    - **Then** I receive a summary via the configured channel
  - **Scenario:** Summary contents
    - **Given** I have received this week's summary
    - **When** I open it
    - **Then** I see (a) number of sessions completed, (b) topics practiced, and (c) a simple progress signal (improved / unchanged / declined)
  - **Scenario:** No-activity week
    - **Given** my child has had zero practice sessions in the past 7 days
    - **When** the weekly delivery time is reached
    - **Then** I still receive a summary noting that there was no activity this week
  - **Scenario:** Channel respects PRD decision
    - **Given** the parent-channel decision (assumption C) has been made
    - **When** the summary is sent
    - **Then** it is delivered via the chosen channel only (not duplicated across channels)

- [ ] **S15 [should] — Mastery change in summary.** As a **parent**, I want the summary to show mastery change week-over-week, so that I can decide whether to keep using the app.
  - Shown as a concrete delta, not a vanity metric.

- [ ] **S16 [nice] — Suggested encouragement prompt.** As a **parent**, I want a suggested encouragement prompt for my child, so that I can support them even though I can't tutor the subject.

## Cross-cutting (guardrails from PRD §3)

- [ ] **S17 [must] — Time-to-first-question ≤ 60s.** As a **student**, I want to be answering my first practice question within 60 seconds of opening the app, so that I don't lose interest before I begin.
  - Measured from app open to first question rendered for a returning student.

  **Acceptance criteria**
  - **Scenario:** Returning student starts a session quickly
    - **Given** I am a returning student with onboarding and diagnostic complete
    - **And** today's session has not yet been started
    - **When** I open the app and tap into today's session
    - **Then** the first question is rendered within 60 seconds of app open (p95 across instrumented sessions)
  - **Scenario:** Instrumentation is in place
    - **Given** the app is running in production
    - **When** a returning student opens it and reaches their first question
    - **Then** the elapsed time is logged as a `time_to_first_question_ms` metric
  - **Scenario:** First-time student excluded
    - **Given** I am a first-time student going through onboarding
    - **When** I open the app
    - **Then** my session is excluded from the time-to-first-question guardrail measurement

- [ ] **S18 [should] — Session reminder.** As a **student** (or via my **parent**'s channel), I want a reminder when I haven't practiced in N days, so that I come back consistently without relying on willpower.
  - Channel and cadence TBD with parent-summary channel decision.

---

## Notes on dependencies

- **S2, S4, S7, S9, S12** all depend on the question bank existing and being topic-tagged. Per PRD review, content sourcing (O3) is the critical path and these stories cannot start until it's resolved.
- **S14, S18** depend on the parent-channel decision (email vs. in-app vs. WhatsApp) which depends on PRD assumption C (primary device).
- **S12, S13** depend on a defined mastery function. Without it these stories are not estimable.
