# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A WhatsApp-bot MVP that delivers a personalized math practice loop to 6th-grade students preparing for a private *secundaria* entrance exam in CDMX. Solo-PM project; the codebase is being built iteratively against the documents in `docs/`. Currently the application code is a minimal scaffold (FastAPI with `/health` and `/webhook` stubs); most of the value is in the product/spec docs that drive what gets built.

## Source-of-truth document hierarchy

These four documents are load-bearing — read them before making non-trivial changes:

1. **`docs/prd.md`** — the PRD. Locks scope, success metrics, MVP, mastery function, and resolved A/B/C decisions. Section §4 defines the mastery function (% correct over last 5 attempts per topic; "mastered" = ≥80%) which must be used identically wherever mastery is computed (no separate display formulas).
2. **`docs/stories.md`** — INVEST user stories with Given/When/Then acceptance criteria. Each `[must]` story has a corresponding GitHub issue (#1–#12). Story IDs (S1, S2, …) are stable and referenced from issues.
3. **`docs/adr/0001-stack.md`** — Stack decision (Twilio + Supabase + Render + Anthropic Claude on Python 3.12 / FastAPI). Includes what's intentionally hard.
4. **`docs/testing.md`** — Pragmatic test strategy. Notable: WhatsApp is not a browser, so end-to-end tests simulate Twilio webhooks rather than using Playwright. The LLM-explanation eval (§d) is the highest-stakes test surface.

PRD/stories/ADR are versioned in their headers — bump versions when changing them.

## Non-obvious project conventions

- **WhatsApp is the only surface.** No web UI, no native app. Stories that look like dashboards (`S5`, `S11`) are auto-rendered PNGs sent as WhatsApp media. Don't propose a browser frontend.
- **All user-facing copy is Mexican Spanish.** Including error messages, button labels, AI-generated explanations.
- **The LLM never generates answers — only explanations grounded in a stored reference answer.** This is a safety-critical constraint (the bot is used unsupervised by minors preparing for a high-stakes exam). The `S9` acceptance criteria enforce it.
- **Off-topic free-text from users does not pass through to the LLM** as an open prompt — see story `S16`. The bot only responds to structured turns and a small set of slash commands.
- **No Twilio / Supabase / Anthropic SDKs in `pyproject.toml` yet** — they will be added in the issues that need them, not preemptively.

## Common commands

Setup:
```
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run dev server (auto-reload):
```
uvicorn sdlc_demo.main:app --reload --port 8000
```

Run all tests:
```
pytest
```

Run a single test:
```
pytest tests/test_health.py::test_health
```

## Code layout

- `src/sdlc_demo/` — application package (src layout; `pythonpath = ["src"]` is set in `pyproject.toml` so tests work without an editable install, though `pip install -e .[dev]` is still recommended).
- `tests/` — pytest tests; uses `fastapi.testclient.TestClient` (httpx under the hood) — no live server needed.
- `docs/` — see hierarchy above.
- `LEARNINGS.md` — phase-by-phase notes on the SDLC demo project itself; usually not relevant to product code changes.

## Repo / workflow conventions

- `main` is protected — direct pushes are rejected. All changes go through PRs.
- Issues are labeled `mvp` plus one of `surface`, `loop`, `content`, `parent`, `ops`. New issues should follow the same convention.
- Branch naming so far: `chore/scaffold` for setup work; expect `feat/sN-…` style for story work (where N is the story ID).
- Commits use Conventional Commits prefixes (`docs:`, `chore:`, `feat:`, `fix:`, `test:`).
