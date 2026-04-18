# PRD: AI Tutor for Mexican *Secundaria* Entrance Exam Prep

**Status:** Draft v0.2
**Last updated:** 2026-04-18
**Owner:** Roberto Bautista

**Change log v0.2:** Locked decisions A (target exam type), B (language), C (surface/device); added a v1 scoping reconciliation in §1; rewrote §4–§5 for the WhatsApp surface; defined mastery function (N=5, ≥80%); updated risks to reflect WhatsApp-specific exposures.

**Change log v0.2.1:** Locked O-school (mid-tier private secundaria in CDMX; first partnership target = La Salle network, single campus) and O-subject (Math).

---

## 1. Problem & user

### Problem (long-term thesis)
6th-grade students in Mexico preparing for *secundaria* entrance exams cannot reliably assess or close gaps in their mastery of exam topics. Human tutoring is financially out of reach for most families, and parents typically lack the time or subject knowledge to coach their child through it. The result is underperformance on a high-stakes placement exam that materially affects which secundaria a child attends.

### v1 scoping decision (read this before reading further)
For v1 we are deliberately **narrowing to one specific private *secundaria*'s entrance exam — a mid-tier private secundaria in CDMX, with the La Salle network as the first partnership target** (single campus; specific campus to be agreed in the partnership conversation; fallback is a comparable single-campus lay/Catholic private secundaria in CDMX with a published exam guide and ≥100 applicants per cycle). This trades wedge fit for shorter time-to-validation: a single, knowable content domain we can author against; a real, scored, high-stakes outcome (admission yes/no) we can measure within one exam cycle; and a feasible partnership/distribution surface. Mid-tier (rather than elite) was deliberately chosen so that families do not already have private tutors — the bot is providing marginal value, not redundant value.

The honest consequence: **v1 will primarily reach scholarship-track and aspirational families taking that one school's exam — not the broader underserved segment described above.** v2 re-targets the underserved wedge once the mastery loop is validated. v1 is a feasibility test of the *mechanism*, not of the *wedge*.

### Primary user (v1)
**6th-grade student, ages 11–12**, preparing for the target private *secundaria*'s entrance exam.
- Practices on the **parent's WhatsApp account** (phone is parent-owned; student is the active conversational party).
- Self-directed practice sessions, often without an adult nearby who can verify answers or explain mistakes.
- Variable reading stamina and attention span; needs short, contained practice loops.

### Secondary user (v1)
**Parent / guardian** (non-paying enabler of the student's use).
- Owns the WhatsApp number the student practices on; sees the same thread the student does.
- Cannot tutor the subject directly but wants visibility into whether their child is improving.
- Decides whether to keep the bot in the family's chat list.

### Long-term user (v2 target — not in v1)
The original underserved-segment family described in the long-term thesis. v2 success requires showing that the v1 mechanism transfers to a different exam (likely a selective public secundaria or regional standardized test) and a less-resourced family.

---

## 2. Goals & non-goals

### Goals (v1)
1. **Diagnose** a student's current mastery across the topics on the target school's exam.
2. **Generate personalized practice** that targets the student's weakest topics first.
3. **Give immediate, subject-accurate feedback** on every attempt, including a worked explanation of the correct answer.
4. **Show progress** in a way the student finds motivating and the parent finds legible — entirely inside WhatsApp.
5. **Work for a student practicing alone**, with no required adult intervention to start, continue, or interpret results.

### Non-goals (this product, not just MVP)
1. **Not a general-purpose study app.** Scope is *secundaria* entrance exam prep — not homework help, not high school prep, not English learning.
2. **Not optimizing for time-on-app.** Engagement-hours is not a success metric. A student who masters the material faster is a better outcome.
3. **Not a replacement for tutors for families who can afford them.** Long-term, the wedge is the underserved segment.

### Non-goals (v1 specifically)
4. **Not a native or web app.** WhatsApp is the only surface.
5. **Not multi-school.** v1 targets one school's exam; broadening is a v2 question.

---

## 3. Success metrics

> Baselines remain **TBD** because the product does not yet exist. Targets below are the bar to clear once the first cohort produces baselines.

### Primary metric
**Admission rate to the target private secundaria** among students who complete ≥6 weeks of practice.
- *Definition:* Percentage of v1 cohort students who applied to the target school and were admitted.
- *Baseline:* TBD — measured against (a) self-reported school-level admission rate, and (b) a non-user comparison cohort if obtainable through the school partnership.
- *Target:* meaningful lift vs. baseline, with effect size to be defined post-baseline. (We commit to publishing the cohort number whether or not the lift is meaningful — no hiding null results.)

### Secondary metrics
| Metric | Baseline | Target |
|---|---|---|
| Mock-exam score lift on a held-out, partnership-sourced practice exam (week 1 → week 8) | TBD | ≥ 15 percentage-point average lift |
| Mastery coverage: % of in-scope topics where student reaches the "mastered" threshold (see §4 for definition) | TBD | ≥ 70% by week 8 |
| Weekly active student rate (of students who completed onboarding) | TBD | ≥ 50% in weeks 1–8 |
| Parent-reported confidence in child's exam readiness (survey, 1–5) | TBD | ≥ 4.0 by week 8 |

> Note on the diagnostic: in v1 we use a **partnership-sourced mock exam** (questions from past exams or school-provided materials, not from our own practice bank) so the practice loop and the diagnostic are not drawn from the same source. This avoids the test-set leakage flagged in the v0.1 review.

### Guardrail metrics (must NOT regress)
- **Median session length** stays ≤ 30 minutes.
- **Hallucination / wrong-answer rate** on graded items < 1% (manually audited sample, against the partnership-sourced answer key).
- **Time-to-first-question from `/start`** ≤ 60 seconds in a fresh chat.
- **WhatsApp Business API cost per active student per month** remains within the agreed unit-economics envelope (specific number TBD with finance).

---

## 4. MVP scope

The MVP is the smallest WhatsApp bot that lets a student go from "I just messaged the bot" to "I have a personalized, working daily practice loop with feedback and a parent-readable progress signal."

### In scope for MVP
1. **Onboarding (in WhatsApp)**
   - Parent (or student) sends an initial message / clicks a deep link.
   - Bot collects: parent acknowledgment of consent, student first name, exam date.
   - Target school is fixed at v1 (no school-selection menu).
2. **Initial diagnostic (chat-delivered)**
   - 20–30 questions sent as a chat sequence using interactive WhatsApp message types (button-list, numbered choice, short text).
   - Coverage: every in-scope topic in the MVP subject for the target school.
   - Output: per-topic mastery estimate stored on the student profile.
3. **Personalized daily practice session**
   - 10–15 questions per day, surfaced as "today's session" via a chat prompt.
   - Question selection weights toward topics where the student's mastery score is lowest.
   - Each question: attempt → immediate correct/incorrect message → AI-generated explanation grounded in the question's reference answer.
4. **Mastery view (on-demand, in chat)**
   - Student or parent sends a `/progreso` (or button) message → bot replies with a per-topic mastery summary, delivered as a text breakdown and an auto-rendered image (PNG) of the topic bars.
   - Includes "what to work on next" — a single recommended topic.
5. **Weekly parent summary (in-thread WhatsApp message)**
   - Sent on the same WhatsApp number the student practices on, addressed to the parent.
   - Contains: sessions completed this week, topics practiced, mastery delta vs. last week, simple progress signal (improved / unchanged / declined), and one suggested encouragement prompt.
6. **Content: Math (Matemáticas), one subject end-to-end.** Picked over Español because (a) closed-form items give a cleaner correctness signal for the mastery loop, (b) reference-answer-grounded explanations work better for math than for reading comprehension (which has interpretation gradients), (c) the image-render pipeline already needed for the mastery view doubles as the math-notation render path, (d) math is heavily weighted on most secundaria entrance exams, and (e) parents read math improvements more easily than Español improvements.

### Mastery function (locked, v1)
- **Definition:** for each topic, mastery = % correct over the **last 5 attempts** on that topic.
- **"Mastered" threshold:** ≥ 80% (i.e., 4 of last 5 correct).
- **Cold-start rule:** until a student has 5 attempts on a topic, mastery is reported as "still learning" with the current % shown.
- **Used everywhere:** the same function drives §3 metrics, §4 question selection, the mastery view, and the parent summary. There is no separate display formula.
- **Planned re-evaluation:** revisit when we have ~10k+ student responses to support a calibrated IRT/BKT model.

### Explicitly NOT in MVP (deferred, not killed)
- Multi-school / multi-exam support.
- Multi-subject coverage beyond the one MVP subject.
- Any non-WhatsApp surface (web, native).
- Multiple students per parent account.
- Voice / audio messages (text + image only in v1).
- Gamification (streaks, badges, leaderboards).
- School / classroom / teacher views.
- Open-ended chat with the model. Practice loop is structured turns only.
- Payments and subscription billing — v1 runs free for the partnership cohort to gather baselines.

---

## 5. Key user flows (WhatsApp)

### Flow A: First-time onboarding → first practice session
1. Parent receives a one-pager from the school (or a WhatsApp deep link) describing the bot.
2. Parent opens the link or sends "hola" to the bot's WhatsApp number.
3. Bot greets, explains in plain Spanish, and asks parent to acknowledge consent (single button reply).
4. Bot asks for student first name and exam date (typed / button-picked).
5. Bot starts the diagnostic — questions delivered as a chat sequence; student can pause and resume by leaving and coming back.
6. After the final diagnostic question, bot sends the results summary (text + auto-rendered image of mastery bars) and a prompt: "¿Empezamos con la práctica de hoy?"
7. Student taps "Sí" → first practice session begins immediately.

### Flow B: Returning daily practice
1. Bot sends a daily nudge ("Hola, ¿lista para tu sesión de hoy? 15 min") at a parent-configured time.
2. Student opens WhatsApp, taps "Empezar" → bot sends question 1.
3. For each question: student taps an answer → bot replies with correct/incorrect + a plain-language explanation grounded in the reference answer → student sees the next question.
4. After question N: bot sends an end-of-session message with mastery delta and the recommended next topic.

### Flow C: Parent weekly check-in
1. Bot sends a weekly summary message addressed to the parent on the same WhatsApp thread (delivered at the parent-configured time).
2. Summary contains: sessions completed, topics practiced, mastery delta, progress signal, and one encouragement prompt.
3. Parent can reply with `/progreso` at any time to get the current mastery view on demand.

### Flow D: Late-joiner (exam in <6 weeks)
1. During onboarding, if the entered exam date is less than 6 weeks away, the bot warns the parent that v1 is designed for ≥6 weeks of practice and may not produce meaningful lift in the available window.
2. Parent confirms ("entendido") → onboarding continues with no UI changes; the student is excluded from the primary-metric cohort but still uses the product.

---

## 6. Out of scope (this release)

- Live human tutor escalation.
- Peer / social features.
- Content for subjects outside the chosen MVP subject.
- Any non-WhatsApp surface (no PWA fallback, no native app).
- Adaptive difficulty *within* a question (no dynamic hint laddering — explanations only after attempt).
- Localization beyond Mexican Spanish.
- School-district sales motion.
- Open-ended LLM chat. The bot only responds to structured turns and a small set of slash commands (`/progreso`, `/pausar`, `/ayuda`).

---

## 7. Assumptions & open questions

### Resolved decisions (v0.2)
| ID | Decision |
|---|---|
| A | Target exam type: **one specific private *secundaria*'s entrance exam**. v1 target = **mid-tier private secundaria in CDMX; first partnership target = La Salle network, single campus**. Fallback: comparable single-campus lay/Catholic CDMX school with a published guide and ≥100 applicants/cycle. |
| B | Language: **Mexican Spanish** for all UI copy, questions, and AI-generated explanations. |
| C | Surface: **WhatsApp Business API** as the only student practice surface and the only parent-summary channel. Account model assumes the *parent's* WhatsApp number is the practice channel. |
| D | MVP subject: **Math (Matemáticas)**, one subject end-to-end. |
| Mastery | **% correct over last 5 attempts per topic; "mastered" = ≥ 80%.** Defined in §4. |

### Remaining assumptions (must be validated)

**E. AI accuracy on the target school's curriculum.** Assumed: a frontier model with careful prompting and a curated reference-answer-grounded explanation pipeline can produce subject-accurate explanations at <1% error rate. To be measured against the partnership-sourced answer key.

**F. Parents accept WhatsApp-mediated unsupervised AI use by their child.** Lower trust burden than a standalone app (already a familiar surface), but still must be validated with the partnership cohort.

**G. WhatsApp Business API approval & policy compatibility.** Assumed: an education bot with no marketing messages and explicit opt-in clears Meta's policy review. To be confirmed by submitting early.

**H. Parent's phone is reliably available for the student's daily 15–20 min session.** Concrete failure mode: student can't practice when parent is at work with their phone. To be validated.

### Open questions

| ID | Question | Blocks |
|---|---|---|
| O-content | Where does the math question bank come from — past exams, school-licensed, AI-generated and human-reviewed, or a hybrid? | Content cost & timeline |
| O-partnership | Open the partnership conversation with La Salle (specific campus); secure past-exam materials and a commitment to share admission outcome data. | Content authoring + primary metric measurement |
| O-cost | What is the WhatsApp Business API cost-per-active-student-per-month at our session volume, and is it viable long-term given v2's underserved-segment goal? | Unit economics |
| O-channel-late | Acquisition channel for v2 once we re-target the underserved segment — does WhatsApp still make sense? | v2 strategy |
| O-business | What is the eventual business model that keeps v2 reachable for the underserved segment? | Long-term viability |

---

## 8. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Wrong target school picked** — content authored against an exam blueprint that doesn't match what the school actually tests. | Medium | High | Resolve O-school via a partnership conversation; require school to share a past exam before authoring begins. |
| **AI gives subject-incorrect explanations** in a high-stakes prep context. | Medium | Very high | Human-reviewed question bank with reference answers; constrain AI to *explain* known-correct answers, not generate them; ongoing audit of a sampled % of explanations against the partnership answer key. |
| **WhatsApp UX cannot deliver the mastery view well** — image-rendered bars feel clunky compared to a native dashboard. | High | Medium | Treat the chat-based mastery view as a v1 compromise; commit to specific quality bars (legibility on a 5-inch screen, rendered in <2s, accurate to the same mastery function). |
| **WhatsApp Business API cost balloons** at scale, killing v2 unit economics. | Medium | High | Track cost per active student weekly from week 1; lock O-cost answer before v2 expansion. |
| **Meta policy change** breaks the bot or restricts education use cases. | Low | Very high | Submit for review early; design content + flows to comply with a strict reading of WhatsApp Business policy; have a fallback channel-design sketch even if not built. |
| **Parent's phone is unavailable** when the student wants to practice (Risk H). | Medium | High | Measure opt-in dropout reasons in onboarding; if this proves a top-3 cause, reconsider B for v2. |
| **Wedge drift made explicit** — v1 by construction doesn't serve the underserved segment named in §1. | Locked-in | High by design | Acknowledged in §1 v1 scoping. v2 must re-target. Track v1 cohort socioeconomic mix in post-launch surveys to set a clear v2 baseline. |
| **Students don't use it consistently** without an adult enforcing it. | High | High | Daily WhatsApp nudge (already a high-attention surface); short complete-in-one-sitting sessions; parent weekly summary creates social accountability. |
| **Content cost balloons** if we author from scratch. | Medium | Medium | Resolve O-content early; prefer school-provided past exams + AI-assisted explanation generation with human review. |
| **Regulatory / child-safety exposure** (LFPDPPP, minor data handling). | Medium | High | Scope a legal review as a deliverable before launch (not a footnote); minimize PII; no open-ended chat with the model; explicit parent consent in onboarding. |
| **Hallucination on math notation** in chat-delivered Spanish-language questions. | Medium | High | Use a reviewed question bank (not LLM-generated) for graded items; LLM is constrained to natural-language explanation only; weekly evaluation harness against held-out items. |

---

## 9. Open decisions to unblock the next step

Before content authoring can start:
- **O-partnership** — La Salle (or fallback) partnership conversation opened; past exam materials in hand.
- **O-content** — math question bank sourcing path decided.

Before engineering can start the bot scaffold:
- **G** — WhatsApp Business API account submitted for review.
- **O-cost** — first-cut cost model agreed (even if rough).

Everything else can evolve as we learn.
