---
name: sdd-constitution
description: Create or update the project constitution at memory/constitution.md from provided principles. Use when the user wants to write, amend, or set up the project constitution or governance principles.
---

## User Input

The input text the user provided in the conversation supplies the principles to add, amend, or establish the constitution with.

You **MUST** consider the user input before proceeding (if not empty).

## Scope Guard

This skill's own work is limited to updating the project constitution itself. Dependent templates and other skills read the constitution at runtime and are not modified here.

- Classify every part of the user input as either constitution content or a separate, non-governance intent.
- If the input includes feature implementation, code generation, refactoring, building, or deployment requests, you **MUST NOT** execute them. Extract them as deferred intents instead.
- You **MUST NOT** create, modify, or delete application source files, feature routes, components, tests, deployment files, or other artifacts unrelated to the constitution workflow.
- If it is unclear whether an instruction is constitution content, ask for clarification before making changes.
- After completing the constitution update, include a `Next Actions` section for each deferred intent. List the original intent and suggest the appropriate follow-up DSH skill (e.g., `sdd-specify`), without invoking it.
- If there are no non-governance intents, omit the `Next Actions` section.

## Outline

You are updating the project constitution at `memory/constitution.md`. The active constitution scaffold is the constitution template (see "Constitution Template Structure" below). If `.specify/memory/constitution.md` already exists, treat it as the source of current project-specific values; otherwise `memory/constitution.md` is the canonical location this skill writes.

Follow this execution flow:

1. **Resolve the active template**:
   - Use the constitution template structure (below) as the required scaffold.
   - If `memory/constitution.md` (or `.specify/memory/constitution.md`) already exists, load it as the source of current project-specific values and amendments. Preserve information that is still applicable when applying the scaffold.
   - If it does not exist, use the resolved template as the initial document.
   - Do not write back to any versioned template layer.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   - **IMPORTANT**: The user might require fewer or more principles than the template provides. If a number is specified, respect it — follow the general template structure and adjust the document accordingly.

2. **Collect/derive values for placeholders**:
   - If the user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown, ask or mark TODO); `LAST_AMENDED_DATE` is today if changes are made, otherwise keep the previous value.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - **MAJOR**: Backward incompatible governance/principle removals or redefinitions.
     - **MINOR**: New principle/section added or materially expanded guidance.
     - **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements.
   - If the version bump type is ambiguous, propose reasoning before finalizing.

3. **Draft the updated constitution content** using the resolved template as the required structure:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots the project has chosen not to define yet — explicitly justify any left).
   - Preserve heading hierarchy; comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section has: a succinct name line, a paragraph (or bullet list) capturing non-negotiable rules, and an explicit rationale if not obvious.
   - Ensure the Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. **Produce a Sync Impact Report** (prepend as an HTML comment at the top of the constitution file after update):
   - Version change: old → new.
   - List of modified principles (old title → new title if renamed).
   - Added sections.
   - Removed sections.
   - Follow-up TODOs if any placeholders intentionally deferred.

5. **Validation before final output**:
   - No remaining unexplained bracket tokens.
   - Version line matches the report.
   - Dates are ISO format `YYYY-MM-DD`.
   - Principles are declarative, testable, and free of vague language (replace "should" with MUST/SHOULD rationale where appropriate).

6. **Write** the completed constitution back to `memory/constitution.md` (overwrite). Write only `memory/constitution.md`; do not create or modify template source files.

7. **Output a final summary** to the user with:
   - New version and bump rationale.
   - Any TODO placeholders or deferred items requiring manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).
   - A `Next Actions` section for any deferred non-governance intents.

## Constitution Template Structure

```
# [PROJECT_NAME] Constitution

## Core Principles
  ### [PRINCIPLE_1_NAME]
  [PRINCIPLE_1_DESCRIPTION]
  ### [PRINCIPLE_2_NAME]
  [PRINCIPLE_2_DESCRIPTION]
  ... (Articles I–IX pattern; IV/V/VI are project-defined)
  ### [PRINCIPLE_5_NAME]  (e.g., V. Observability / VI. Versioning / VII. Simplicity)
  [PRINCIPLE_5_DESCRIPTION]

## [SECTION_2_NAME]  (e.g., Additional Constraints, Security Requirements, Performance Standards)
  [SECTION_2_CONTENT]

## [SECTION_3_NAME]  (e.g., Development Workflow, Review Process, Quality Gates)
  [SECTION_3_CONTENT]

## Governance
  [GOVERNANCE_RULES]
  **Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
```

## Formatting & Style Requirements

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info is missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include it in the Sync Impact Report under deferred items.

**Next**: after updating the constitution, invoke the `sdd-specify` skill to implement a feature specification based on the updated constitution.

## Done When

- [ ] Constitution written to `memory/constitution.md` with Sync Impact Report.
- [ ] Validation passed (no unexplained bracket tokens, version matches report, ISO dates).
- [ ] Final summary with version bump rationale, TODOs, and Next Actions reported to user.

---
_Ported from [GitHub Spec-Kit](https://github.com/github/spec-kit) `templates/commands/constitution.md` (CC0/MIT). Licensed under MIT — see repository LICENSE. Logic preserved for DeepSeek Harness skill execution._