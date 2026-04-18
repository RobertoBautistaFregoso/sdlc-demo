# MVP User Stories

**Version:** v0.2 (rewritten for WhatsApp surface per PRD v0.2 §4)
Source: `docs/prd.md` §4 (MVP scope) and §5 (key user flows).

**Tags:** `[must]` blocks MVP launch · `[should]` MVP needs it to be useful · `[nice]` defer if time-pressed.

**INVEST applied:** each story is independently shippable, negotiable, user-valuable, estimable in <1 sprint, small, and testable.

**Personas:**
- *Student* — 6th-grade student, ages 11–12, the active practice user.
- *Parent* — owns the WhatsApp number the student practices on; receives the weekly summary.

**Surface:** every story below ships inside WhatsApp. There is no app, no web UI, no dashboard outside WhatsApp.

**Mastery function (locked, per PRD §4):** % correct over last 5 attempts per topic; "mastered" = ≥ 80%.

---

## Account & onboarding

- [ ] **S1 [must] — Onboard a new student via WhatsApp.** As a **parent**, I want to onboard my child by messaging the bot once, so that they can start practicing without installing anything.
  - No app install; the WhatsApp number is the entire surface.
  - Bot handles parent consent, student name, and exam date in a guided chat sequence.
  - Onboarding state persists if the parent leaves and comes back.

  **Acceptance criteria**
  - **Scenario:** Parent starts a fresh chat with the bot
    - **Given** the parent has not previously messaged the bot from this WhatsApp number
    - **When** the parent sends "hola" (or taps a deep link)
    - **Then** the bot replies with a Spanish welcome message and a single "Empezar" button
  - **Scenario:** Consent is required and explicit
    - **Given** the parent is in onboarding
    - **When** the bot asks for consent acknowledgment
    - **Then** the parent must tap "Acepto" before any further question is asked
    - **And** "Acepto" + the timestamp + the WhatsApp number are stored as the consent record
  - **Scenario:** Onboarding can be resumed
    - **Given** the parent has answered some onboarding questions and then left the chat
    - **When** the parent returns and sends any message
    - **Then** the bot resumes from the next unanswered onboarding step (does not restart)
  - **Scenario:** Required fields collected
    - **Given** onboarding is complete
    - **When** the student profile is inspected
    - **Then** it contains: parent consent record, student first name, exam date, and the WhatsApp number as the channel identifier

- [ ] **S2 [must] — Set exam date during onboarding.** As a **parent**, I want to enter my child's exam date during onboarding, so that the bot can pace practice.
  - Date is editable later via a slash command.
  - Date drives the late-joiner warning in S3.

  **Acceptance criteria**
  - **Scenario:** Parent enters a future exam date
    - **Given** the parent is at the exam-date step of onboarding
    - **When** the parent types or picks a date that is at least 1 day in the future
    - **Then** the date is saved on the student profile and the bot advances to the diagnostic
  - **Scenario:** Parent enters a date in the past
    - **Given** the parent is at the exam-date step
    - **When** the parent enters a date that is in the past
    - **Then** the bot replies with an error message in Spanish and re-prompts for the date
  - **Scenario:** Parent updates the date later
    - **Given** the student is past onboarding
    - **When** the parent sends `/fecha` and provides a new date
    - **Then** the new date replaces the old one and the bot confirms the change

- [ ] **S3 [must] — Late-joiner warning.** As a **parent**, I want to be warned during onboarding if the exam is less than 6 weeks away, so that I have realistic expectations about what the bot can do in the time available.
  - Warning is informational; the parent can continue and use the bot anyway.
  - Late-joiner students are excluded from the primary-metric cohort (per PRD §3).

  **Acceptance criteria**
  - **Scenario:** Exam date is less than 6 weeks away
    - **Given** the parent has just entered an exam date
    - **When** the date is less than 42 days from today
    - **Then** the bot sends a warning in Spanish explaining the v1 design assumes ≥6 weeks of practice
    - **And** the bot asks the parent to confirm with a single "Entendido" button before continuing
  - **Scenario:** Exam date is ≥ 6 weeks away
    - **Given** the parent has just entered an exam date
    - **When** the date is 42 days or more from today
    - **Then** no warning is shown; onboarding continues directly
  - **Scenario:** Late-joiner cohort exclusion
    - **Given** a student onboarded with an exam date <42 days away
    - **When** the analytics cohort is built
    - **Then** that student is flagged as "late_joiner" and excluded from the primary-metric calculation

## Initial diagnostic

- [ ] **S4 [must] — Take the initial diagnostic in chat.** As a **student**, I want to take a one-time diagnostic delivered as a chat sequence, so that the bot knows where I stand before practice begins.
  - Delivered inside the same WhatsApp thread, one question at a time.
  - Uses WhatsApp interactive message types (button list / numbered choice) where the question allows.
  - Produces a per-topic mastery estimate stored on the student profile.

  **Acceptance criteria**
  - **Scenario:** Student completes the diagnostic
    - **Given** onboarding is complete and the student has not yet taken the diagnostic
    - **When** the student answers all diagnostic questions in the chat sequence
    - **Then** a per-topic mastery value (per the §4 mastery function) is computed and stored
    - **And** the bot sends the diagnostic results summary (S5)
  - **Scenario:** Diagnostic length is bounded
    - **Given** the diagnostic for the target school has been generated
    - **When** the question set is inspected
    - **Then** the count is between 20 and 30 inclusive
  - **Scenario:** Diagnostic covers every in-scope topic
    - **Given** the diagnostic has been generated
    - **When** topic coverage is inspected
    - **Then** every in-scope topic for the MVP subject is represented by at least one question
  - **Scenario:** Diagnostic is one-time per student
    - **Given** the student has completed the diagnostic
    - **When** the student returns later
    - **Then** the bot does not re-prompt the diagnostic; it goes straight to today's session or the home prompt

- [ ] **S5 [must] — Diagnostic results summary in chat.** As a **student**, I want a clear results message right after the diagnostic, so that I understand my starting point before I start practicing.
  - Delivered as a text breakdown plus an auto-rendered PNG image of mastery bars.
  - Includes a one-line "what to focus on first" recommendation.

  **Acceptance criteria**
  - **Scenario:** Results sent immediately after diagnostic
    - **Given** the student has just answered the final diagnostic question
    - **When** the bot processes the result
    - **Then** the results message is sent within the same conversational turn (no extra prompt required)
  - **Scenario:** Per-topic mastery is visible
    - **Given** the student has received the results message
    - **When** the student reads the message
    - **Then** every in-scope topic is shown with its current mastery value, both as text and on the rendered image
  - **Scenario:** "Focus on first" is surfaced
    - **Given** the student has received the results message
    - **When** the student reads the message
    - **Then** a single-sentence recommendation names the topic to start with
  - **Scenario:** Image render quality
    - **Given** the results PNG has been rendered
    - **When** displayed at WhatsApp's default image-preview size on a 5-inch phone
    - **Then** topic names and bar values are legible without tapping to enlarge

- [ ] **S6 [should] — Pause and resume diagnostic.** As a **student**, I want to leave the diagnostic mid-way and pick it up later, so that I can complete it across sittings.
  - WhatsApp's nature already lets the student walk away; this story makes the resume explicit.

  **Acceptance criteria**
  - **Scenario:** Student leaves and returns
    - **Given** the student has answered some diagnostic questions and then stopped replying for ≥1 hour
    - **When** the student sends any message in the thread
    - **Then** the bot reminds the student of progress so far ("vas en X de Y") and re-sends the next unanswered question

## Practice loop

- [ ] **S7 [must] — Daily personalized session in chat.** As a **student**, I want a daily session of 10–15 questions delivered in chat and weighted toward my weakest topics, so that I spend time on what matters most.
  - Question selection driven by the §4 mastery function: weight inversely with current mastery.
  - Session estimated at 15–20 min; completable in one sitting.

  **Acceptance criteria**
  - **Scenario:** Session offered on student return
    - **Given** the student has completed the diagnostic
    - **And** the student has not yet completed today's session
    - **When** the student opens the WhatsApp thread (or the daily nudge fires)
    - **Then** the bot offers "today's session" with question count and estimated duration
  - **Scenario:** Session length is bounded
    - **Given** today's session has been generated
    - **When** the question set is inspected
    - **Then** the count is between 10 and 15 inclusive
  - **Scenario:** Weakest topics are prioritized
    - **Given** today's session has been generated
    - **And** topics are ranked by current mastery
    - **When** the topic distribution of the session is inspected
    - **Then** topics in the bottom mastery quartile are represented more frequently than topics in the top quartile
  - **Scenario:** One session per day
    - **Given** the student has completed today's session
    - **When** the student returns later the same calendar day
    - **Then** the bot tells the student today's session is done and indicates when the next one will be available

- [ ] **S8 [must] — Immediate correct/incorrect message after each answer.** As a **student**, I want to see whether each answer was right or wrong immediately in chat, so that I know how I'm doing.
  - Feedback message sent in the same turn as the answer; before the next question.

  **Acceptance criteria**
  - **Scenario:** Correct answer
    - **Given** the student is mid-session
    - **When** the student submits the correct answer
    - **Then** the bot sends a "correct" message before the next question
  - **Scenario:** Incorrect answer
    - **Given** the student is mid-session
    - **When** the student submits an incorrect answer
    - **Then** the bot sends an "incorrect" message that names the correct answer, before the next question
  - **Scenario:** Cannot skip past feedback
    - **Given** the student has just submitted an answer
    - **When** the student tries to advance (e.g., sends arbitrary text)
    - **Then** the next question is not sent until the feedback message has been delivered

- [ ] **S9 [must] — Plain-language explanation grounded in the reference answer.** As a **student**, I want a plain-language explanation of the right answer in chat, so that I can learn from each mistake without an adult nearby.
  - Explanation generated from the question's stored reference answer (not free-form generation).
  - Reading level appropriate for a 6th-grade student (specific level TBD).
  - Sent as a follow-up message within the same feedback turn as S8.

  **Acceptance criteria**
  - **Scenario:** Explanation accompanies feedback
    - **Given** the student has just received correct/incorrect feedback (S8)
    - **When** the bot continues the turn
    - **Then** a plain-language Spanish explanation of the correct answer is sent as a follow-up message
  - **Scenario:** Explanation defends the reference answer
    - **Given** an explanation has been generated for a question
    - **When** the explanation is reviewed against the question's stored reference answer
    - **Then** the explanation defends the reference answer and does not propose a different one
  - **Scenario:** Explanation availability
    - **Given** the student has answered any question (correctly or incorrectly)
    - **When** the feedback turn completes
    - **Then** an explanation is delivered in 100% of cases (no silent fallback to "no explanation available")
  - **Scenario:** Reading-level guardrail
    - **Given** an explanation has been generated
    - **When** measured against the agreed reading-level rubric
    - **Then** it meets the agreed grade-level target

- [ ] **S10 [should] — End-of-session mastery delta message.** As a **student**, I want a message at the end of each session showing what changed in my mastery, so that I feel my effort produced real progress.
  - Sent automatically after the final question of the session.
  - Includes per-topic delta and the next recommended topic.

  **Acceptance criteria**
  - **Scenario:** Delta sent at end of session
    - **Given** the student has just answered the final question of today's session
    - **When** the feedback for that question completes
    - **Then** the bot sends an end-of-session message showing per-topic mastery deltas vs. session start
    - **And** names the next recommended topic
  - **Scenario:** No regression-only framing
    - **Given** the student's mastery declined on some topics this session
    - **When** the end-of-session message is rendered
    - **Then** declines are shown honestly but not as the headline; the headline is the largest improvement (or, if none, an encouraging factual summary)

## Mastery view (on-demand)

- [ ] **S11 [must] — On-demand mastery view via `/progreso`.** As a **student** (or **parent**), I want to send `/progreso` and get my current mastery view as a chat reply, so that I can check progress whenever I want.
  - Reply contains a per-topic text breakdown and an auto-rendered PNG of the bars.
  - Reflects the current mastery values per the §4 function.

  **Acceptance criteria**
  - **Scenario:** Student requests progress
    - **Given** the student has completed the diagnostic
    - **When** the student sends `/progreso`
    - **Then** the bot replies in the same turn with a text breakdown + a PNG image of the mastery bars
  - **Scenario:** Pre-diagnostic state
    - **Given** the student has not yet completed the diagnostic
    - **When** any user sends `/progreso`
    - **Then** the bot replies with a message asking to complete the diagnostic first, not an empty image
  - **Scenario:** Values match the mastery function
    - **Given** the bars are rendered
    - **When** any value is recomputed manually from the last 5 attempts per topic
    - **Then** the displayed value matches (no separate display-only formula)
  - **Scenario:** "What to work on next" is surfaced
    - **Given** the mastery view has been sent
    - **When** the message is read
    - **Then** a single-line recommendation names the next topic to focus on

## Parent visibility

- [ ] **S12 [must] — Weekly parent summary message.** As a **parent**, I want a weekly summary message in the same WhatsApp thread, so that I can tell whether the bot is working without needing to understand the subject.
  - Same WhatsApp number as the student practices on; addressed to the parent.
  - Contains: sessions completed, topics practiced, mastery delta, simple progress signal.

  **Acceptance criteria**
  - **Scenario:** Summary delivered weekly with activity
    - **Given** the student has had at least one practice session in the past 7 days
    - **When** the configured weekly delivery time is reached
    - **Then** a summary message is sent in the WhatsApp thread, explicitly addressed to the parent
  - **Scenario:** Summary contents
    - **Given** the parent has just received this week's summary
    - **When** the parent reads it
    - **Then** the message contains (a) sessions completed, (b) topics practiced, (c) mastery delta vs. last week, and (d) a simple progress signal (mejoró / igual / bajó)
  - **Scenario:** No-activity week
    - **Given** the student has had zero practice sessions in the past 7 days
    - **When** the weekly delivery time is reached
    - **Then** a summary is still sent, noting no activity this week
  - **Scenario:** Single channel
    - **Given** the configured weekly delivery time is reached
    - **When** the summary is sent
    - **Then** it is sent exactly once via WhatsApp (no duplication via email or other channels)

- [ ] **S13 [should] — Encouragement prompt in summary.** As a **parent**, I want a suggested encouragement prompt in the summary, so that I can support my child even though I can't tutor the subject.

  **Acceptance criteria**
  - **Scenario:** Prompt included
    - **Given** the parent has just received this week's summary
    - **When** the parent reads it
    - **Then** the message contains exactly one Spanish-language encouragement prompt the parent can say to their child

## Cross-cutting (guardrails)

- [ ] **S14 [must] — Time-to-first-question ≤ 60s for returning student.** As a **student**, I want my daily session to start within 60 seconds of opening the chat, so that I don't lose interest before I begin.
  - Measured from `session_start_event` (student opens the thread or taps the daily nudge) to `first_question_sent`.

  **Acceptance criteria**
  - **Scenario:** Returning student starts the session quickly
    - **Given** the student is past onboarding and diagnostic
    - **And** today's session has not yet been started
    - **When** the student opens the WhatsApp thread or taps the daily nudge
    - **Then** the first question is sent within 60 seconds (p95 across instrumented sessions)
  - **Scenario:** Instrumentation in place
    - **Given** the bot is in production
    - **When** any returning student starts a session
    - **Then** the elapsed time is logged as a `time_to_first_question_ms` metric
  - **Scenario:** First-time student excluded
    - **Given** the student is in onboarding or the diagnostic
    - **When** the metric is computed
    - **Then** the session is excluded from the guardrail measurement

- [ ] **S15 [should] — Daily session reminder.** As a **student**, I want a daily WhatsApp message reminding me to practice, so that I come back consistently.
  - Sent at a parent-configurable time (default: 18:00 local).
  - Quiet on weekends (default off; parent can enable).

  **Acceptance criteria**
  - **Scenario:** Daily nudge fires
    - **Given** the student has not yet practiced today
    - **When** the configured local time is reached
    - **Then** the bot sends a single short reminder message
  - **Scenario:** No nudge after practice
    - **Given** the student has already completed today's session
    - **When** the configured local time is reached
    - **Then** no reminder is sent

- [ ] **S16 [must] — Off-topic / open-ended messages handled safely.** As a **safety guardrail**, I want the bot to refuse open-ended chat gracefully, so that minors are not chatting freely with an LLM.
  - Bot responds only to: structured practice turns, defined slash commands (`/progreso`, `/fecha`, `/pausar`, `/ayuda`), and known onboarding steps.
  - Anything else gets a polite Spanish refusal pointing back to what the bot can do.

  **Acceptance criteria**
  - **Scenario:** Off-topic free-text message
    - **Given** the student is past onboarding
    - **When** the student sends a message that is not an answer to a current question and not a recognized command
    - **Then** the bot replies with a brief Spanish message listing what it can help with, and does not pass the message to the LLM as an open prompt
  - **Scenario:** Unsafe content attempt
    - **Given** the student sends a message containing content the safety filter flags
    - **When** the bot processes the message
    - **Then** the bot responds with a refusal message and the event is logged for review

---

## Notes on dependencies (from PRD v0.2.1)

- **Subject is locked: Math.** All math-content stories assume math-only scope.
- **Target school is locked at the type level:** mid-tier private secundaria in CDMX (first partnership target = La Salle network, single campus). Specific campus + past-exam materials still pending the partnership conversation (PRD `O-partnership`).
- **S2, S4, S5, S7, S9, S11** all depend on the math question bank (with topic tags + reference answers) for the target school's exam. Per PRD `O-content` and `O-partnership`, content sourcing is the critical path.
- **S1, S12, S15** depend on WhatsApp Business API approval (PRD assumption G).
- **S5, S11** depend on a chosen image-rendering pipeline for the mastery PNG. The same pipeline will render math notation in question content, so a single tech-design pass covers both.
- **S9, S16** depend on the LLM provider + safety/eval harness being in place.
