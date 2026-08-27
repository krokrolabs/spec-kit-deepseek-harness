---
name: sdd-plan
description: Generate the implementation plan (plan.md) and Phase 0/1 design artifacts (research.md, data-model.md, contracts/, quickstart.md) for a feature spec. Use when the user wants to plan, design, or architect a feature.
---

## User Input

The input text the user provided in the conversation (e.g., a tech-stack hint like "I am building with PostgreSQL and WebSocket") guides technical choices.

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup — locate the feature directory**:
   - Read `.specify/feature.json` for `feature_directory`. If absent, infer the most recently created `specs/` feature directory, or ask the user which feature to plan.
   - Set:
     - `FEATURE_SPEC` = `FEATURE_DIR/spec.md`
     - `IMPL_PLAN` = `FEATURE_DIR/plan.md`
     - `SPECS_DIR` = `specs/`
     - `BRANCH` = the current git branch name (created during `sdd-specify`).
   - Abort with an error if `FEATURE_SPEC` (spec.md) does not exist; instruct the user to invoke the `sdd-specify` skill first.

2. **Load context**:
   - Read `FEATURE_SPEC` and `memory/constitution.md` (if it exists).
   - Copy the plan template structure (see "Plan Template Structure" below) into `IMPL_PLAN` as the starting point.

3. **Execute plan workflow**: Follow the structure in the `IMPL_PLAN` template to:
   - Fill the **Technical Context** section (mark unknowns as `NEEDS CLARIFICATION`).
   - Fill the **Constitution Check** section from the constitution.
   - Evaluate the **Phase -1 gates** (Simplicity, Anti-Abstraction, Integration-First — see below); ERROR if violations are unjustified.
   - **Phase 0**: Generate `research.md` (resolve all `NEEDS CLARIFICATION`).
   - **Phase 1**: Generate `data-model.md`, `contracts/`, `quickstart.md`.
   - Re-evaluate the Constitution Check post-design.

## Plan Template Structure

The `plan.md` produced has this structure — preserve it:

```
# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `specs/[###-feature-name]/spec.md`

## Summary
  [Extract from feature spec: primary requirement + technical approach from research]

## Technical Context
  **Language/Version**: [e.g., Python 3.11 or NEEDS CLARIFICATION]
  **Primary Dependencies**: [e.g., FastAPI or NEEDS CLARIFICATION]
  **Storage**: [e.g., PostgreSQL or N/A]
  **Testing**: [e.g., pytest or NEEDS CLARIFICATION]
  **Target Platform**: [e.g., Linux server or NEEDS CLARIFICATION]
  **Project Type**: [library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]
  **Performance Goals**: [domain-specific or NEEDS CLARIFICATION]
  **Constraints**: [domain-specific or NEEDS CLARIFICATION]
  **Scale/Scope**: [domain-specific or NEEDS CLARIFICATION]

## Constitution Check
  *GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
  [Gates determined based on constitution file]

## Project Structure
  ### Documentation (this feature)
    specs/[###-feature]/
    ├── plan.md              # this file
    ├── research.md          # Phase 0 output
    ├── data-model.md        # Phase 1 output
    ├── quickstart.md        # Phase 1 output
    ├── contracts/           # Phase 1 output
    └── tasks.md             # Phase 2 output (sdd-tasks, NOT created here)
  ### Source Code (repository root)
    [Concrete layout for this feature — choose single project, web app, or mobile+api]

## Complexity Tracking
  > Fill ONLY if Constitution Check has violations that must be justified
  | Violation | Why Needed | Simpler Alternative Rejected Because |
```

## Phase -1 Gates (Pre-Implementation)

These gates are enforced by the constitution. Evaluate them before Phase 0 research; document any justified violation in the `Complexity Tracking` section.

### Simplicity Gate (Article VII)
- [ ] Using ≤3 projects?
- [ ] No future-proofing?

### Anti-Abstraction Gate (Article VIII)
- [ ] Using framework directly (rather than wrapping it)?
- [ ] Single model representation?

### Integration-First Gate (Article IX)
- [ ] Contracts defined?
- [ ] Contract tests planned?

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context**:
   - For each `NEEDS CLARIFICATION` → a research task.
   - For each dependency → a best-practices task.
   - For each integration → a patterns task.

2. **Generate and dispatch research subagents**: For each unknown / technology choice / integration, spawn a DSH subagent via the `subagent` tool to research it. Example task briefs:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

   Run independent research subagents in parallel where they have no dependency on each other.

3. **Consolidate findings** in `research.md` using this format per item:
   - **Decision**: [what was chosen]
   - **Rationale**: [why chosen]
   - **Alternatives considered**: [what else was evaluated]

**Output**: `research.md` with all `NEEDS CLARIFICATION` resolved.

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete.

1. **Extract entities from the feature spec** → `data-model.md`:
   - Entity name, fields, relationships.
   - Validation rules from requirements.
   - State transitions if applicable.

2. **Define interface contracts** (if the project has external interfaces) → `contracts/`:
   - Identify what interfaces the project exposes to users or other systems.
   - Document the contract format appropriate for the project type.
   - Examples: public APIs for libraries, command schemas for CLI tools, endpoints for web services, grammars for parsers, UI contracts for applications.
   - Skip if the project is purely internal (build scripts, one-off tools, etc.).

3. **Create quickstart validation guide** → `quickstart.md`:
   - Document runnable validation scenarios that prove the feature works end-to-end.
   - Include prerequisites, setup commands, test/run commands, and expected outcomes.
   - Use links or references to contracts and data model details instead of duplicating them.
   - Do not include full implementation code, model/service/controller bodies, migrations, or complete test suites.
   - Keep this artifact as a validation/run guide; implementation details belong in `tasks.md` and the implementation phase.

**Output**: `data-model.md`, `contracts/*`, `quickstart.md`.

## Key rules

- Use absolute paths for filesystem operations; use project-relative paths for references in documentation.
- ERROR on gate failures or unresolved clarifications.
- Command ends after Phase 1 design.

## Completion Report

Report the branch, `IMPL_PLAN` path, and generated artifacts (`research.md`, `data-model.md`, `contracts/`, `quickstart.md`).

**Next**: invoke the `sdd-tasks` skill to break the plan into an actionable, dependency-ordered task list.

## Done When

- [ ] Plan workflow executed and design artifacts generated.
- [ ] Phase -1 gates evaluated; violations justified or errors raised.
- [ ] Completion reported to user with branch, plan path, and generated artifacts.

---
_Ported from [GitHub Spec-Kit](https://github.com/github/spec-kit) `templates/commands/plan.md` (CC0/MIT). Licensed under MIT — see repository LICENSE. Logic preserved for DeepSeek Harness skill execution._