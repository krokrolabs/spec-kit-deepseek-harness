---
name: sdd-tasks
description: Generate an actionable, dependency-ordered tasks.md for a feature from its plan.md and spec.md. Use when the user wants to break a plan into tasks or create a task list.
---

## User Input

The input text the user provided in the conversation (e.g., context or constraints for task generation) guides prioritization and scope.

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup — locate the feature directory**:
   - Read `.specify/feature.json` for `feature_directory`. If absent, infer the most recently created `specs/` feature directory, or ask the user which feature to task.
   - Set `FEATURE_DIR` to the resolved feature directory (absolute path).
   - Determine `AVAILABLE_DOCS` by listing the documents actually present under `FEATURE_DIR` (e.g., `research.md`, `data-model.md`, `contracts/`, `quickstart.md`).
   - Load the tasks template structure (see "Tasks Template Structure" below) as the scaffold for `tasks.md`.

2. **Load design documents**: Read from `FEATURE_DIR`:
   - **Required**: `plan.md` (tech stack, libraries, structure), `spec.md` (user stories with priorities).
   - **Optional**: `data-model.md` (entities), `contracts/` (interface contracts), `research.md` (decisions), `quickstart.md` (test scenarios).
   - **IF EXISTS**: Load `memory/constitution.md` for project principles and governance constraints.
   - Note: Not all projects have all documents. Generate tasks based on what's available.
   - If `plan.md` or `spec.md` is missing, abort and instruct the user to run `sdd-plan` (missing plan) or `sdd-specify` (missing spec) first.

3. **Execute task generation workflow**:
   - Load `plan.md` and extract tech stack, libraries, project structure.
   - Load `spec.md` and extract user stories with their priorities (P1, P2, P3, etc.).
   - If `data-model.md` exists: extract entities and map to user stories.
   - If `contracts/` exists: map interface contracts to user stories.
   - If `research.md` exists: extract decisions for setup tasks.
   - Generate tasks organized by user story (see Task Generation Rules below).
   - Generate a dependency graph showing user story completion order.
   - Create parallel execution examples per user story.
   - Validate task completeness (each user story has all needed tasks, independently testable).

4. **Generate tasks.md**: Use the tasks template structure as the scaffold. Fill with:
   - Correct feature name from `plan.md`.
   - Phase 1: Setup tasks (project initialization).
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories).
   - Phase 3+: One phase per user story (in priority order from `spec.md`).
   - Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks.
   - Final Phase: Polish & cross-cutting concerns.
   - All tasks must follow the strict checklist format (see Task Generation Rules below).
   - Clear file paths for each task.
   - Dependencies section showing story completion order.
   - Parallel execution examples per story.
   - Implementation strategy section (MVP first, incremental delivery).

## Tasks Template Structure

The `tasks.md` produced has this structure — preserve it:

```
# Tasks: [FEATURE NAME]

**Input**: Design documents from `specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Tests are OPTIONAL — only include if explicitly requested.
**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`
  - **[P]**: Can run in parallel (different files, no dependencies)
  - **[Story]**: Which user story (e.g., US1, US2)
  - Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)
## Phase 2: Foundational (Blocking Prerequisites) — BLOCKS all user stories
## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP
  ### Tests for User Story 1 (OPTIONAL)
  ### Implementation for User Story 1
  **Checkpoint**: ...
## Phase 4..N: User Story 2, 3, ... (Priority: P2, P3, ...)
## Phase N: Polish & Cross-Cutting Concerns
## Dependencies & Execution Order
## Parallel Example: User Story 1
## Implementation Strategy (MVP First / Incremental Delivery / Parallel Team)
## Notes
```

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if the user requests a TDD approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox).
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order.
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks).
4. **[Story] label**: REQUIRED for user story phase tasks only.
   - Format: [US1], [US2], [US3], etc. (maps to user stories from `spec.md`).
   - Setup phase: NO story label.
   - Foundational phase: NO story label.
   - User Story phases: MUST have story label.
   - Polish phase: NO story label.
5. **Description**: Clear action with exact file path.

**Examples**:

- ✅ CORRECT: `- [ ] T001 Create project structure per implementation plan`
- ✅ CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ WRONG: `- [ ] Create User model` (missing ID and Story label)
- ❌ WRONG: `T001 [US1] Create model` (missing checkbox)
- ❌ WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- ❌ WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From User Stories (spec.md)** — PRIMARY ORGANIZATION:
   - Each user story (P1, P2, P3...) gets its own phase.
   - Map all related components to their story: models, services, interfaces/UI, and (if requested) tests.
   - Mark story dependencies (most stories should be independent).

2. **From Contracts**:
   - Map each interface contract → the user story it serves.
   - If tests requested: each interface contract → contract test task `[P]` before implementation in that story's phase.

3. **From Data Model**:
   - Map each entity to the user story(ies) that need it.
   - If an entity serves multiple stories: put it in the earliest story or the Setup phase.
   - Relationships → service layer tasks in the appropriate story phase.

4. **From Setup/Infrastructure**:
   - Shared infrastructure → Setup phase (Phase 1).
   - Foundational/blocking tasks → Foundational phase (Phase 2).
   - Story-specific setup → within that story's phase.

### Phase Structure

- **Phase 1**: Setup (project initialization).
- **Phase 2**: Foundational (blocking prerequisites — MUST complete before user stories).
- **Phase 3+**: User Stories in priority order (P1, P2, P3...).
  - Within each story: Tests (if requested) → Models → Services → Endpoints → Integration.
  - Each phase should be a complete, independently testable increment.
- **Final Phase**: Polish & Cross-Cutting Concerns.

## Completion Report

Output the path to the generated `tasks.md` and a summary:
- Total task count.
- Task count per user story.
- Parallel opportunities identified.
- Independent test criteria for each story.
- Suggested MVP scope (typically just User Story 1).
- Format validation: confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths).

The `tasks.md` should be immediately executable — each task must be specific enough that an LLM can complete it without additional context.

**Next**: invoke the `sdd-analyze` skill to run a consistency analysis across spec/plan/tasks, or load the `sdd-implement` skill to start implementation.

## Done When

- [ ] `tasks.md` generated with all phases, task IDs, and file paths.
- [ ] Completion reported to user with task count, story breakdown, and MVP scope.

---
_Ported from [GitHub Spec-Kit](https://github.com/github/spec-kit) `templates/commands/tasks.md` (CC0/MIT). Licensed under MIT — see repository LICENSE. Logic preserved for DeepSeek Harness skill execution._