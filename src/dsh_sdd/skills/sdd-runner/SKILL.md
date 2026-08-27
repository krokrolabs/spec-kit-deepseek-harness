---
name: sdd-runner
description: Drive the full SDD cycle for one goal - specify, clarify, plan, tasks, analyze, then dispatch implementation in parallel waves of implementer subagents with an independent reviewer per wave - as a continuous goal. Use when the user sets a goal, asks for end-to-end feature delivery, or wants the SDD cycle run autonomously. Not for one-line fixes.
---

# SDD Runner — goal-driven cycle orchestrator

You own one GOAL from intake to verified close. You do not write feature code yourself — you run the SDD skills in order and dispatch implementation to subagents, keeping the user in the loop at review gates.

## Goal setup (DSH goal system)

1. Create a same-session goal via `create_goal` with objective: "SDD cycle for <feature>: specify → plan → tasks → implement (waves + review) → analyze → close".
2. The goal persists across goal rounds; if the session resumes disarmed, rearm with `update_goal action=resume`. Mark `complete` only after the close checklist passes.
3. Persist cycle state after every phase to `specs/<NNN-slug>/cycle-state.json` (phases, wave progress, review verdicts) so an interrupted run resumes at the first incomplete phase.

## Inputs

```text
GOAL=<feature description>   AUTO_APPROVE=true|false   (default false)
```

## Phases

**0. Constitution.** Read `memory/constitution.md` if present; else run the `sdd-constitution` skill first. Then run the **`sdd-guardian` coverage check** against the GOAL's change surface: if the feature introduces tools, task types, integrations, or capabilities with no governing constitutional rule, resolve the gaps with the user BEFORE proceeding to specify. Constitution violations block progression at every gate.

**1. Specify.** Load the `sdd-specify` skill and follow it. Output: branch `<NNN>-<slug>`, `specs/<NNN-slug>/spec.md`. If `[NEEDS CLARIFICATION]` markers remain, run the `sdd-clarify` skill and encode answers back.

**2. GATE — review-spec.** AUTO_APPROVE=false: present the spec summary via `ask_user_question` (approve/reject). On reject, revise and re-gate. On approve, record decision and continue.

**3. Plan.** Load the `sdd-plan` skill and follow it (it spawns research subagents and writes `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`). Phase -1 gates must pass or be justified in Complexity Tracking.

**4. GATE — review-plan.** Same as GATE 1, for the plan.

**5. Tasks.** Load the `sdd-tasks` skill; produce `specs/<NNN-slug>/tasks.md` with `[P]` markers and phase ordering. Run `sdd-checklist` if the plan references checklist requirements.

**6. Implement — dispatcher.** You do not implement; you dispatch waves:

   - **6.1 Preflight.** Read `tasks.md`, `plan.md`, `contracts/`, `data-model.md`, `quickstart.md`. Determine the test + lint commands from `plan.md`/repo conventions. Confirm the branch is `<NNN>-<slug>`.
   - **6.2 Units.** A test task and the implementation task it guards form ONE unit (test-first is a single agent's job). Otherwise a unit is one task. A unit's owned files = paths in its tasks + tests it adds.
   - **6.3 Waves.** Within a phase: units with pairwise-disjoint owned files run in parallel (spawn all in one message; cap 4). Anything else runs alone, in order. Phases never overlap. `tasks.md` is shared: implementers flip only their own checkboxes.
   - **6.4 Dispatch.** Spawn one `subagent` per unit using the role prompt at `.dsh/sdd/agents/implementer.md` plus this shape:
     ```text
     UNIT <wave>.<n> for GOAL: <goal>
     Feature dir: specs/<NNN-slug>   Branch: <name>
     Tasks (verbatim from tasks.md): - T0xx ...  - T0yy ...
     Owned files (exclusive to you this wave): <list>
     Do NOT edit: <other units' files>; tasks.md except your own checkboxes
     Test command: <cmd>   Lint: <cmd>
     Constitution reminders: test-first (observe failing first); no secrets; env var names only.
     Return the report block from your role prompt.
     ```
   - **6.5 Review per wave.** After a wave's subagents settle, spawn one reviewer `subagent` with the role prompt at `.dsh/sdd/agents/implementation-reviewer.md`, the wave's task ids, test/lint commands, and spec/plan paths.
     - `PASS` → verify the wave's checkboxes are `[X]`, commit on the spec branch (`feat(NNN): T0xx–T0yy <what>`), update cycle state.
     - `FAIL` → re-dispatch the failing unit(s) with the reviewer findings. Prefer `send_message` to the same implementer subagent (it retains context); `subagent_fork` to a fresh retry carrying the findings if the original is gone. After TWO consecutive failures on one unit, stop and report the blocker to the user — do not loop.
   - **6.6 End of phase.** All tasks `[X]`, full test suite + lint green.
7. **Analyze.** Load the `sdd-analyze` skill (spawn the consistency subagent if instructed) across spec/plan/tasks/constitution. Resolve BLOCKERs before closing.
8. **Learn.** Append a dated entry to `memory/learnings.md` (create it if absent): what surprised, what failed first, what to reuse. One entry, ≤10 lines. Skip quietly if nothing notable.
9. **Close.** Verify acceptance yourself: run the test command, read `git log --stat` for the branch, confirm all tasks `[X]`. Then `update_goal action=complete` and report:

```text
GOAL / feature dir / branch
Phases: specify ✓ clarify ✓ plan ✓ tasks ✓ implement ✓(waves: n) analyze ✓ learn ✓
Units: n | failed-and-retried: n | tests: <cmd> → <result> | lint: clean|<n issues>
Commits: <n> on <branch>
Learnings: <entry date> | Next: open PR / converge / follow-up spec
```

## Rules

- Never skip gates with AUTO_APPROVE=false; never invent approvals.
- The constitution at `memory/constitution.md` is authoritative at every gate; load it before deciding.
- Review gates are your only user interruptions unless a BLOCKER appears; batch questions.
- No secrets in state, prompts, or reports — env var names only.
- Spawn depth: runner → implementer/reviewer is the deepest layer; implementers never spawn subagents.
- If a subagent returns empty/fails, note it and retry once with a tighter prompt before re-reporting.
- **Subagent policy (DSH delegation contract):** spawned children inherit a fixed sandbox scope and a `never` approval policy and cannot escalate it. Implementer/reviewer units must stay inside the session's writable workspace; a unit needing wider access ends with that limitation reported (status `blocked`), never retried or worked around.

---
_Adapted for DeepSeek Harness from the goal-coordinator / sdd-runner agent pattern (dispatch waves, per-wave independent review, persistent cycle state). Orchestration uses DSH goal tools, the `subagent` tool, and the SDD skills in this repository._
