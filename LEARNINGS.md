# Learnings — SDLC Demo

One line per phase. What surprised me, what worked, what I'd do differently.

---

## Phase 0 — Environment & project shell

**Playbook steps:**
1. `mkdir ~/dev/sdlc-demo && cd ~/dev/sdlc-demo`
2. `git init -b main`
3. Open the folder in IDE; launch Claude Code (`claude` in integrated terminal).
4. Ask Claude which MCP servers and skills are available.
5. Create `LEARNINGS.md` with a single header.

**My notes:**
- what MCP servers and Skills I have available
- how the project directory folder was set up

---

## Phase 1 — Idea & problem framing

**Playbook steps:**
1. Invoke `/product-management:brainstorm`. Let Claude interview you. Pick something small with a real user.
2. Ask Claude to write a one-paragraph problem statement, target user, and three non-goals to `docs/idea.md`.
3. Commit: `git add . && git commit -m "chore: problem statement and MVP framing"`

**My notes:**
-

---

## Phase 2 — Requirements & PRD

**Playbook steps:**
1. Run `/product-management:write-spec`. Feed it `docs/idea.md`. Produce `docs/prd.md`.
2. Plan mode (Shift+Tab twice). Ask Claude to critique the PRD. Iterate until satisfied.
3. Ask Claude to break the PRD into user stories using INVEST criteria → `docs/stories.md` with `[must]`/`[should]`/`[nice]` tags.
4. Ask Claude to define acceptance criteria for each `[must]` story in Given/When/Then format.
5. Commit.

**My notes:**
-

---

## Phase 3 — Technical design

**Playbook steps:**
1. Run `/engineering:architecture`. Ask Claude to propose 2–3 stacks ranked by "shortest path to shipping." Pick one.
2. Ask Claude to write `docs/adr/0001-stack.md` with the decision, rejected alternatives, and consequences.
3. Run `/engineering:testing-strategy` to draft `docs/testing.md` (unit + one e2e happy path).
4. Commit.

**My notes:**
-

---

## Phase 4 — GitHub setup & backlog

**Playbook steps:**
1. `gh repo create sdlc-demo --private --source=. --remote=origin --push`
2. Ask Claude to read `docs/stories.md` and create one GitHub issue per `[must]` story with `gh issue create`, using acceptance criteria as body and `mvp` label.
3. Optional: `gh project create --owner "@me" --title "SDLC Demo"` and link issues.
4. Enable branch protection on `main` (UI or `gh api`). Require PRs to merge.
5. Commit docs written so far.

**My notes:**
-

---

## Phase 5 — Scaffold & `/init`

**Playbook steps:**
1. Ask Claude to scaffold your chosen stack (minimal). Specify language, framework, DB, tests.
2. Run the dev server (`preview_start` or manual). Verify it loads; screenshot via `preview_screenshot`.
3. Run `/init` → generates `CLAUDE.md`. Trim what's wrong, add what's missing.
4. First real commit + push.

**My notes:**
-

---

## Phase 6 — Feature loop

Repeat per `[must]` story:

**Playbook steps:**
1. **Branch:** `git checkout -b feat/<short-name>`
2. **Plan:** Enter plan mode. Paste the issue body. Ask Claude to write a plan file before editing. Review.
3. **Build:** Exit plan mode; let Claude implement. Watch the TodoWrite list.
4. **Verify in browser/client:** Use `preview_start` / `preview_click` / `preview_snapshot` (or curl for webhook apps).
5. **Test:** Unit test for core logic + integration test for happy path. Run both.
6. **Commit:** Small, clear messages. Let Claude draft; you edit.
7. **PR:** `gh pr create`. Link the issue with `Closes #<n>`.
8. **Review:** On the PR branch, run `/review` and `/security-review`. Resolve findings.
9. **Merge:** Squash-merge. Confirm the issue auto-closed.
10. **LEARNINGS.md:** One line on what Claude got right/wrong this loop.

**My notes:**
-

---

## Phase 7 — CI/CD & deployment

**Playbook steps:**
1. Ask Claude to add a GitHub Actions workflow (install, typecheck, unit tests, e2e tests) on PRs and `main`. Review YAML before committing.
2. Push. Watch the Action run: `gh run watch`.
3. Connect the repo to the deploy target (Vercel/Render/etc.). Auto-deploy `main`.
4. Run `/engineering:deploy-checklist` before your next deploy. Fix whatever it flags.
5. Merge a trivial change and confirm the live URL updates.

**My notes:**
-

---

## Phase 8 — Feedback & iteration

**Playbook steps:**
1. Share the deployed URL with 2–3 people. Capture feedback in `docs/feedback.md`.
2. Run `/product-management:synthesize-research` on the file to extract themes.
3. Turn the top 1–2 themes into new issues (`gh issue create`).
4. Run `/engineering:tech-debt` on the repo. Decide: fix now, or file an issue for later?
5. Optional: save `feedback` and `project` memories.

**My notes:**
-

---

## Phase 9 — Retrospective

**Playbook steps:**
1. Open `LEARNINGS.md`. Group entries into: *surprised me / worked well / friction / would do differently*.
2. Ask Claude: "Based on `LEARNINGS.md`, what three workflow improvements should I make for the next project? Propose concrete changes to my CLAUDE.md or hooks."
3. Save worthwhile improvements to your `~/.claude/` global config.

**My notes:**
-
