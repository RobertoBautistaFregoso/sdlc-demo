# ADR 0001 — v1 Tech Stack

**Status:** Accepted
**Date:** 2026-04-18
**Owner:** Roberto Bautista

## Context

PRD v0.2.1 commits v1 to a WhatsApp-only surface (assumption C) delivering a personalized math practice loop to 6th-grade students preparing for a mid-tier private *secundaria* entrance exam in CDMX. Success requires shipping a real, end-to-end mastery loop (diagnostic → practice → reference-grounded explanations → mastery view → weekly parent summary) fast enough to gather cohort data within one exam cycle (PRD §3 primary metric: admission rate to the target school). The stack must therefore optimize for *time-to-cohort-data* by a solo PM, not for long-run unit economics.

## Decision

**Stack A: Twilio + Supabase + Render + Anthropic.**

| Layer | Choice | Version |
|---|---|---|
| Surface | WhatsApp via **Twilio Programmable Messaging** (sandbox number for dev) | Twilio Python SDK 9.x |
| Backend | **Python 3.12 + FastAPI** | FastAPI 0.115.x |
| DB | **Supabase Postgres**, managed | Postgres 16 |
| LLM | **Anthropic Claude Sonnet 4.6** (`claude-sonnet-4-6`), with prompt caching on per-question reference + system prompt | Anthropic Python SDK 0.40+ |
| Image rendering | **matplotlib** for mastery PNGs; **KaTeX → SVG → PNG** for math notation in question content | matplotlib 3.9; KaTeX 0.16 |
| Hosting | **Render** — web service (webhook), cron job (daily nudges), background worker if needed | n/a (managed) |
| Auth | **None app-level.** WhatsApp number is identity. Twilio HMAC-signs inbound webhooks; that is the auth boundary. | n/a |

In parallel with v1 dev, submit Meta Business Manager verification so the Twilio → Meta-direct migration is unblocked when v2 economics demand it.

## Rejected alternatives

- **Stack B — Meta WhatsApp Cloud API direct + Fly.io + Postgres + Claude.** Better long-run unit economics, but Meta business verification + template approval is calendar-time work that bottlenecks a solo PM and risks missing the exam cycle.
- **Stack C — Wati / BuilderBot + Vercel functions + Supabase + Claude.** Fastest to first deploy, but the platform's flow-builder abstraction breaks down on the rolling-window mastery loop — you drop to webhook code by day 5, having paid for lock-in *and* still written the same backend.

## Consequences

**What becomes easy**
- End-to-end dev against the Twilio sandbox without waiting on Meta verification.
- Stateful logic (mastery, attempts, cohort analytics) lives in normal Postgres tables — trivial to query, debug, and back up.
- Git-push deploys; built-in TLS; cron jobs and workers without spinning up infra.
- Identity is solved by construction: WhatsApp number = student profile.
- Image rendering and explanation generation share a single backend, so the math-notation pipeline (S5/S11 in stories) is the same code path as the mastery view.

**What becomes hard**
- **Per-message cost**: Twilio's per-WhatsApp-message fee stacks on top of Meta's per-conversation cost. Unit economics will tighten before the cohort data is in. Mitigation: instrument `cost_per_active_student_per_month` from week 1; design the data layer to be Twilio-agnostic so the Meta-direct migration is mechanical, not architectural.
- **Vendor coupling to Twilio's WhatsApp message-template format** — moving to Meta-direct later means re-approving templates.
- **No native dashboards or admin UI** — operating the system means SQL against Supabase. Acceptable for v1 scale; revisit if cohort grows past a few hundred students.
- **LLM latency budget is tight** inside a WhatsApp turn (target <2s round trip). Need prompt caching from day 1, not as an optimization later.
