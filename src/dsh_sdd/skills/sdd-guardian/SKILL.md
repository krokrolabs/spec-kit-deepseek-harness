---
name: sdd-guardian
description: Constitution coverage check at work intake. When the user asks to add or implement a new tool, task, integration, capability, or feature, recall the constitution at memory/constitution.md, verify the change is governed by existing principles, and if something new has no governing rule, ask the user to define or amend it BEFORE continuing. Use whenever new work starts.
---

# Constitution Guardian — coverage gate at intake

You are the constitution's watchdog. Nothing new enters this codebase ungoverned. Run this check at the start of any new tool, task, integration, capability, or feature request — **before** implementation begins.

## Procedure

### 1. Intake inventory

Restate what is about to be added in one or two lines, then list its **change surface**:

- What is touched: tools, subagents, configuration surface, external services, data, auth/permissions, tests, deployment.
- What it demands: new library/dependency, new network egress, new credentials/secrets, new file locations, new review requirements.

### 2. Load the constitution

Read `memory/constitution.md` (fallback: `.specify/memory/constitution.md`).

- **If no constitution exists**: do not block, but tell the user — "no constitution found; recommend running the `sdd-constitution` skill to establish one" — and use `ask_user_question` to offer: (a) establish constitution now, (b) proceed ungoverned this once (record the decision in a dated `memory/learnings.md` note so it is not silently forgotten).

### 3. Coverage check

Build a coverage table, one row per change-surface item:

| Change-surface item | Governing article/section | Covered / Gap |
|---|---|---|

Cite the constitution's own wording for each "Covered" row. A rule that names the general area is covered; vague adjacency is a Gap.

### 4. Gap handling — ask BEFORE continuing

For every Gap row, draft a minimal candidate principle (one declarative, testable sentence + rationale, matching the constitution's style) and present all gaps together via `ask_user_question` with options per gap:

- **Adopt proposed principle** (default) — add via a MINOR constitution amendment using the `sdd-constitution` skill (version bump + Sync Impact Report), then continue the original task.
- **User edits the principle** — take the user's wording, amend via `sdd-constitution`, then continue.
- **Proceed without a rule** — allowed only with explicit user confirmation; record the justification in the constitution's Complexity Tracking / exceptions note and in `memory/learnings.md`.

Never implement a gap-class change before one of these three outcomes is recorded.

### 5. Covered case

If every row is Covered: state the governing rules briefly as implementation reminders (e.g., "test-first applies to the new tool — Art. III"; "no new config keys without constitution coverage — Governance") and hand off to the requested work.

## Rules

- This skill checks **coverage only** — it never writes feature code; its file writes are limited to constitution amendments (via `sdd-constitution`) and the learnings note.
- Batch all gaps into one interaction; do not interrogate the user one question at a time.
- One reminder at most per covered rule; do not restate the whole constitution.
- If the original request was a new SDD feature (spec-worthy), end by suggesting the `sdd-specify` / `sdd-runner` skills once coverage is resolved.

## Output

```text
Change: <one line>
Coverage: <n> covered / <n> gaps
Gaps → <amended: principle text + version bump | user-approved exception | pending user input>
Governing rules for this work: <list>
Proceed: yes | waiting on user
```

---
_Added for the DSH adaptation: constitutional coverage is enforced continuously at intake, not only at plan-time gates. The constitution remains the architecture DNA; this guardian makes sure new kinds of work acquire rules before they acquire code._
