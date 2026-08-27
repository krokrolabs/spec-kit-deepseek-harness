---
name: sdd-analyze
description: Perform a read-only cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation. Use when the user wants to analyze, audit, or check consistency of SDD artifacts.
---

## User Input

The input text the user provided in the conversation can scope or focus the analysis (e.g., a specific domain or concern).

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation. This skill MUST run only after `sdd-tasks` has successfully produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (the user must explicitly approve before any follow-up editing skills would be invoked manually).

**Constitution Authority**: The project constitution (`memory/constitution.md`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks — not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update via the `sdd-constitution` skill, outside `sdd-analyze`.

## Execution Steps

### 1. Initialize Analysis Context

- Read `.specify/feature.json` for `feature_directory`. If absent, infer the most recently created `specs/` feature directory, or ask the user which feature to analyze.
- Derive absolute paths:
  - `SPEC` = `FEATURE_DIR/spec.md`
  - `PLAN` = `FEATURE_DIR/plan.md`
  - `TASKS` = `FEATURE_DIR/tasks.md`
- Abort with an error message if any required file is missing (instruct the user to run the missing prerequisite skill — `sdd-specify`, `sdd-plan`, or `sdd-tasks`).

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**
- Overview/Context
- Functional Requirements
- Success Criteria (measurable outcomes — e.g., performance, security, availability, user success, business impact)
- User Stories
- Edge Cases (if present)

**From plan.md:**
- Architecture/stack choices
- Data Model references
- Phases
- Technical constraints

**From tasks.md:**
- Task IDs
- Descriptions
- Phase grouping
- Parallel markers [P]
- Referenced file paths

**From constitution:**
- Load `memory/constitution.md` for principle validation.

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: For each Functional Requirement (FR-###) and Success Criterion (SC-###), record a stable key. Use the explicit FR-/SC- identifier as the primary key when present, and optionally also derive an imperative-phrase slug for readability (e.g., "User can upload file" → `user-can-upload-file`). Include only Success Criteria items that require buildable work (e.g., load-testing infrastructure, security audit tooling), and exclude post-launch outcome metrics and business KPIs (e.g., "Reduce support tickets by 50%").
- **User story/action inventory**: Discrete user actions with acceptance criteria.
- **Task coverage mapping**: Map each task to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases).
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements.

### 4. Detection Passes (Token-Efficient Analysis)

Focus on high-signal findings. Limit to 50 findings total; aggregate the remainder in an overflow summary.

#### A. Duplication Detection
- Identify near-duplicate requirements.
- Mark lower-quality phrasing for consolidation.

#### B. Ambiguity Detection
- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria.
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`, etc.).

#### C. Underspecification
- Requirements with verbs but missing object or measurable outcome.
- User stories missing acceptance criteria alignment.
- Tasks referencing files or components not defined in spec/plan.

#### D. Constitution Alignment
- Any requirement or plan element conflicting with a MUST principle.
- Missing mandated sections or quality gates from the constitution.

#### E. Coverage Gaps
- Requirements with zero associated tasks.
- Tasks with no mapped requirement/story.
- Success Criteria requiring buildable work (performance, security, availability) not reflected in tasks.

#### F. Inconsistency
- Terminology drift (same concept named differently across files).
- Data entities referenced in plan but absent in spec (or vice versa).
- Task ordering contradictions (e.g., integration tasks before foundational setup tasks without dependency note).
- Conflicting requirements (e.g., one requires Next.js while other specifies Vue).

### 5. Severity Assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: Violates a constitution MUST, missing core spec artifact, or a requirement with zero coverage that blocks baseline functionality.
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion.
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case.
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order.

### 6. Produce Compact Analysis Report

Output a Markdown report (no file writes) with the following structure:

```
## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |
```

(Add one row per finding; generate stable IDs prefixed by the category initial.)

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Metrics:**
- Total Requirements
- Total Tasks
- Coverage % (requirements with >=1 task)
- Ambiguity Count
- Duplication Count
- Critical Issues Count

### 7. Provide Next Actions

At the end of the report, output a concise Next Actions block:
- If CRITICAL issues exist: recommend resolving before `sdd-implement`.
- If only LOW/MEDIUM: the user may proceed, but provide improvement suggestions.
- Provide explicit skill suggestions: e.g., "Re-run `sdd-specify` with refinement", "Run `sdd-plan` to adjust architecture", "Manually edit `tasks.md` to add coverage for 'performance-metrics'".

### 8. Offer Remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically.)

## Operating Principles

### Context Efficiency
- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation.
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis.
- **Token-efficient output**: Limit findings table to 50 rows; summarize overflow.
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts.

### Analysis Guidelines
- **NEVER modify files** (this is read-only analysis).
- **NEVER hallucinate missing sections** (if absent, report them accurately).
- **Prioritize constitution violations** (these are always CRITICAL).
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns).
- **Report zero issues gracefully** (emit a success report with coverage statistics).

## Done When

- [ ] All three core artifacts analyzed across detection passes.
- [ ] Compact analysis report with coverage summary, metrics, and Next Actions produced.
- [ ] Remediation offered (without auto-applying).

---
_Ported from [GitHub Spec-Kit](https://github.com/github/spec-kit) `templates/commands/analyze.md` (CC0/MIT). Licensed under MIT — see repository LICENSE. Logic preserved for DeepSeek Harness skill execution._