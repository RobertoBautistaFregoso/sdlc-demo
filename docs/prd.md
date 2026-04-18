# PRD: AI Tutor for Mexican *Secundaria* Entrance Exam Prep

**Status:** Draft v0.1
**Last updated:** 2026-04-18
**Owner:** Roberto Bautista

---

## 1. Problem & user

### Problem
6th-grade students in Mexico preparing for *secundaria* entrance exams cannot reliably assess or close gaps in their mastery of exam topics. Human tutoring is financially out of reach for most families, and parents typically lack the time or subject knowledge to coach their child through it. The result is underperformance on a high-stakes placement exam that materially affects which secundaria a child attends.

### Primary user
**6th-grade student in Mexico, ages 11–12**, preparing for a private or selective public *secundaria* entrance exam.
- Self-directed study sessions, often without an adult nearby who can verify answers or explain mistakes.
- Variable reading stamina and attention span; needs short, contained practice loops.
- Owns or shares access to a device (see assumption C).

### Secondary user
**Parent / guardian** (non-paying enabler of the student's use).
- Cannot tutor the subject matter directly, but wants visibility into whether their child is improving and whether time spent on the app is producing results.
- Decides whether to keep using the product.

### Evidence / signals (to validate during discovery)
- Cost of in-person tutoring in Mexico vs. household income for the target segment.
- Parent willingness to let a child use an AI tool unsupervised.
- Existence and pricing of incumbent prep options (workbooks, group classes, YouTube channels).

> *This section currently relies on the founder's domain knowledge. Open question O1 below tracks the discovery work needed to ground it in data.*

---

## 2. Goals & non-goals

### Goals (what success looks like for the MVP)
1. **Diagnose** a student's current mastery across the topics on their target exam.
2. **Generate personalized practice** that targets the student's weakest topics first.
3. **Give immediate, subject-accurate feedback** on every attempt, including a worked explanation of the correct answer.
4. **Show progress** in a way the student finds motivating and the parent finds legible.
5. **Work for a student studying alone**, with no required adult intervention to start, continue, or interpret results.

### Non-goals (explicitly out of scope for this product, not just the MVP)
1. **Not a general-purpose study app.** Scope is *secundaria* entrance exam prep — not homework help, not high school prep, not English learning.
2. **Not optimizing for time-on-app.** Engagement-hours is not a success metric. A student who masters the material faster is a better outcome.
3. **Not a replacement for tutors for families who can afford them.** The wedge is the underserved segment; we are not building a premium tutor-replacement for middle/upper-class families.

---

## 3. Success metrics

> Baselines below are marked **TBD** because the product does not yet exist and we do not yet have a measured cohort. The first 4–6 weeks post-launch establish baselines; targets below are the bar we want to clear *against* those baselines.

### Primary metric
**Diagnostic-score lift over 8–12 weeks of use.**
- *Definition:* Percentage-point change in score on a held-out, exam-aligned diagnostic between week 1 and week 8–12 of consistent use.
- *Baseline:* TBD (measured from first cohort).
- *Target:* ≥ 15 percentage-point average lift among students with ≥ 3 sessions/week.

### Secondary metrics
| Metric | Baseline | Target |
|---|---|---|
| Mastery coverage: % of in-scope topics where student reaches "mastered" threshold | TBD | ≥ 70% by week 12 |
| Weekly active student rate (of students who completed onboarding) | TBD | ≥ 50% in weeks 1–8 |
| Parent-reported confidence in child's exam readiness (survey, 1–5) | TBD | ≥ 4.0 by week 8 |
| Real exam placement rate vs. comparable non-user baseline | TBD | Meaningful lift (effect size to be defined post-baseline) |

### Guardrail metrics (must NOT regress)
- **Median session length** stays ≤ 30 minutes. Longer sessions would suggest we're chasing engagement instead of mastery.
- **Hallucination / wrong-answer rate** on graded items < 1% (manually audited sample).
- **Time-to-first-practice-question** from app open ≤ 60 seconds.

---

## 4. MVP scope

The MVP is the smallest product that lets a single student go from "I have an exam coming up" to "I have a personalized, working practice loop with feedback."

### In scope for MVP
1. **Student onboarding**
   - Pick target exam (from a short curated list — see assumption A).
   - Pick target exam date.
2. **Initial diagnostic**
   - ~20–30 question adaptive diagnostic covering in-scope subjects.
   - Produces a per-topic mastery estimate.
3. **Personalized practice session**
   - "Today's session" surfaces 10–15 questions weighted toward weakest topics.
   - Each question: attempt → immediate correct/incorrect → AI-generated explanation of the right answer in plain language.
4. **Mastery dashboard (student view)**
   - Per-topic mastery bars.
   - "What to work on next."
5. **Parent summary (lightweight)**
   - Weekly email or in-app summary: topics practiced, mastery change, suggested encouragement.
6. **Content: one subject end-to-end** for the MVP (likely Spanish/*Español* or Math — to be decided after exam target is locked, see O2).

### Explicitly NOT in MVP (deferred, not killed)
- Multi-subject coverage beyond the one MVP subject.
- Multiple students per parent account.
- Offline mode.
- Voice / read-aloud.
- Gamification (streaks, badges, leaderboards).
- School / classroom / teacher views.
- Payments and subscription billing — MVP runs free for an initial cohort to gather baselines.

---

## 5. Key user flows

### Flow A: First-time student onboarding → first practice session
1. Student opens app for the first time (parent may help with sign-up).
2. Picks target exam from a short list.
3. Picks exam date.
4. Takes the initial diagnostic (~15–25 minutes, can pause and resume).
5. Sees a "here's where you are" summary: per-topic mastery + an estimate of how much practice will close the gap by exam date.
6. Starts first personalized practice session immediately, or schedules a reminder.

### Flow B: Returning student daily practice loop
1. Student opens app.
2. Sees "Today's session" — 10–15 questions, est. 15–20 min.
3. For each question: attempts → submits → sees correct/incorrect + plain-language explanation → optional "ask why" follow-up.
4. End of session: sees what changed in mastery, what's next.

### Flow C: Parent weekly check-in
1. Parent receives weekly summary (email or notification).
2. Sees: sessions completed this week, topics practiced, mastery delta, one suggested conversation prompt for their child.
3. Optional: opens the parent dashboard for more detail.

---

## 6. Out of scope (this release)

- Live human tutor escalation.
- Peer/social features.
- Content for subjects outside the chosen MVP subject.
- Native mobile apps if the primary device decision (assumption C) lands on web.
- Adaptive difficulty *within* a question (e.g., dynamic hint laddering) — explanations only after attempt.
- Localization beyond the language decision in assumption B.
- School-district sales motion.

---

## 7. Assumptions & open questions

### Assumptions (load-bearing, must be validated)

**A. Specific *secundaria* exam target — PLACEHOLDER.**
The MVP will target one specific entrance exam, not "*secundaria* entrance exams" in general. The exam dictates the topic blueprint, question style, and difficulty calibration. *To be specified by founder.* Candidates likely include: COMIPEMS (CDMX/EdoMex public-school placement), specific private-school entrance exams, or a state-specific equivalent. Until this is locked, content scope and diagnostic design are blocked.

**B. Spanish-language assumption — PLACEHOLDER.**
Assumed default: the entire product UI, instructional copy, questions, and AI-generated explanations are in **Mexican Spanish**. *To be confirmed by founder.* This affects model choice, prompt design, content authoring, and any third-party content licensing.

**C. Primary device & distribution channel — PLACEHOLDER.**
*To be specified by founder.* Open candidates:
- Mobile web (works on a shared family Android phone, no install friction).
- Native Android (better UX, install friction, Play Store distribution).
- Desktop web (assumes household has a laptop — likely wrong for the target segment).
This decision drives the entire frontend stack, offline strategy, and parent-facing distribution channel (WhatsApp link? App store? School flyer?).

**D. Subject scope for MVP.** Assumed: one subject, end-to-end, before broadening. To be picked once A is locked.

**E. AI accuracy on Mexican curriculum content.** Assumed: a frontier model with careful prompting and a curated question bank can produce subject-accurate explanations at <1% error rate on graded items. To be measured.

**F. Unsupervised use is acceptable to parents.** Assumed: parents in the target segment will allow a child to use this without sitting next to them. To be validated in user research.

### Open questions

| ID | Question | Blocks |
|---|---|---|
| O1 | What does discovery with 8–10 target families actually surface re: current prep behavior, willingness to pay, and device access? | Validates problem framing |
| O2 | Which subject ships first in the MVP (likely Math or Español)? | Content authoring |
| O3 | Where does the question bank come from — authored from scratch, licensed, or AI-generated and human-reviewed? | Content cost & timeline |
| O4 | How do we measure "real exam placement rate" without waiting a full exam cycle? Proxy diagnostic? | Primary metric validation |
| O5 | Free during MVP — but what's the eventual business model that keeps the product reachable for the underserved segment? | Long-term viability |

---

## 8. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Wrong exam picked** — we build for an exam that doesn't match what the target segment is actually taking. | Medium | High | Resolve assumption A before content work begins. Validate with 8–10 target families. |
| **AI gives subject-incorrect explanations**, eroding trust with parents and producing harm to students preparing for a high-stakes exam. | Medium | Very high | Human-reviewed question bank with reference answers; constrain AI to explain *known-correct* answers rather than generate them; ongoing audit of a sampled % of explanations. |
| **Students don't use it consistently** without an adult enforcing it. | High | High | Design for short, complete-in-one-sitting sessions; parent weekly nudge; explicit "what to do today" surface; do not rely on intrinsic motivation alone. |
| **Parent can't tell if it's working**, churns the child off the product before mastery gains compound. | Medium | High | Parent weekly summary with concrete mastery deltas, not vanity metrics. |
| **Device assumption is wrong** (assumption C) — we ship for a device the segment doesn't have reliable access to. | Medium | Very high | Resolve assumption C with field research, not desk research. |
| **Content cost balloons** if we author from scratch per exam. | Medium | Medium | Decide O3 early; consider AI-assisted authoring with human review for v1. |
| **Regulatory / child-safety exposure** from an AI product used unsupervised by minors. | Low–Medium | High | Review applicable Mexican data-protection (LFPDPPP) and minor-safety requirements before launch; minimize PII collection; no open-ended chat with the model. |
| **Equity drift**: if the product ends up most useful to families who already have devices, time, and a quiet study space, we miss the wedge. | Medium | High | Track usage by self-reported segment; explicitly design for low-bandwidth, shared-device, low-parent-availability cases. |

---

## 9. Open decisions to unblock the next step

Before this PRD can drive engineering work, we need:
- **A** (target exam) — locked.
- **B** (language) — confirmed.
- **C** (primary device) — decided.
- **O2** (MVP subject) — picked, downstream of A.

Everything else can evolve as we learn.
