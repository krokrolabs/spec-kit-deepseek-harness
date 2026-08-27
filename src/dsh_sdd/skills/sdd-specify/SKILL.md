---
name: sdd-specify
description: Turn a feature description into a DSH SDD feature spec (spec.md) under specs/<NNN-slug>/ with a new git branch. Use when the user wants to specify, spec out, or write a feature specification.
---

## User Input

The feature description **is** the input text the user provided in the conversation. Assume you always have it available even if the conversation is terse. Do not ask the user to repeat it unless they provided nothing at all (empty).

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Given the feature description the user provided in the conversation, do this:

1. **Generate a concise short name** (2-4 words) for the feature:
   - Analyze the feature description and extract the most meaningful keywords.
   - Create a 2-4 word short name that captures the essence of the feature.
   - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug").
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.).
   - Keep it concise but descriptive enough to understand the feature at a glance.
   - Examples:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **Create the spec feature directory**:
   - Specs live under the default `specs/` directory.
   - Auto-generate the directory name under `specs/`:
     - Scan existing directories in `specs/` to determine the next available 3-digit sequential number `NNN` (e.g., `001`, `002`, …; expand beyond 3 digits automatically when needed).
     - Construct the directory name: `<NNN>-<short-name>` (e.g., `003-user-auth`).
     - Set `FEATURE_DIR` to `specs/<NNN>-<short-name>`.
   - Create the directory (and any needed parents).

3. **Create a git branch**:
   - Create a git branch named `<NNN>-<short-slug>` (using the same `NNN` and short-name slug as the feature directory).
   - The spec directory name and the git branch name are independent but here intentionally share the prefix/slug.

4. **Create the spec file**:
   - Resolve the active spec template (see the "Spec Template Structure" section below) and copy it to `FEATURE_DIR/spec.md` as the starting point.
   - Set `SPEC_FILE` to `FEATURE_DIR/spec.md`.
   - Persist the resolved feature directory path to `.specify/feature.json`:
     ```json
     {
       "feature_directory": "<resolved feature dir, e.g. specs/003-user-auth>"
     }
     ```
     This allows downstream skills (`sdd-plan`, `sdd-tasks`, etc.) to locate the feature directory.

   **IMPORTANT**:
   - You must only create one feature per `sdd-specify` invocation.
   - The spec directory and file are always created by this skill.

5. Load the active spec template (below) to understand required sections.

6. **IF EXISTS**: Load `memory/constitution.md` for project principles and governance constraints.

7. Follow this execution flow:
   1. Parse the feature description from the user input.
      - If empty: ERROR "No feature description provided".
   2. Extract key concepts from the description.
      - Identify: actors, actions, data, constraints.
   3. For unclear aspects:
      - Make informed guesses based on context and industry standards.
      - Only mark with `[NEEDS CLARIFICATION: specific question]` if:
        - The choice significantly impacts feature scope or user experience.
        - Multiple reasonable interpretations exist with different implications.
        - No reasonable default exists.
      - **LIMIT: Maximum 3 `[NEEDS CLARIFICATION]` markers total**.
      - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details.
   4. Fill the User Scenarios & Testing section.
      - If no clear user flow: ERROR "Cannot determine user scenarios".
   5. Generate Functional Requirements.
      - Each requirement must be testable.
      - Use reasonable defaults for unspecified details (document assumptions in the Assumptions section).
   6. Define Success Criteria.
      - Create measurable, technology-agnostic outcomes.
      - Include both quantitative metrics (time, performance, volume) and qualitative measures (user satisfaction, task completion).
      - Each criterion must be verifiable without implementation details.
   7. Identify Key Entities (if data involved).
   8. Return: SUCCESS (spec ready for planning).

8. Write the specification to `SPEC_FILE` using the template structure, replacing placeholders with concrete details derived from the feature description while preserving section order and headings.

## Spec Template Structure

The resolved spec template (`spec.md`) has this structure — preserve section order and headings:

```
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [DATE]
**Status**: Draft
**Input**: User description: "<the feature description the user provided>"

## User Scenarios & Testing *(mandatory)*
  User stories PRIORITIZED as user journeys ordered by importance (P1, P2, P3...).
  Each story must be INDEPENDENTLY TESTABLE — implementing just ONE yields a viable MVP.
  ### User Story N - [Brief Title] (Priority: PN)
    [Describe this user journey in plain language]
    **Why this priority**: ...
    **Independent Test**: ...
    **Acceptance Scenarios**: Given/When/Then
  ### Edge Cases
    - What happens when [boundary condition]?
    - How does system handle [error scenario]?

## Requirements *(mandatory)*
  ### Functional Requirements
    - **FR-001**: System MUST [specific capability]
    - mark unclear: **FR-006**: System MUST authenticate via [NEEDS CLARIFICATION: ...]
  ### Key Entities *(include if feature involves data)*
    - **[Entity]**: [what it represents, key attributes without implementation]

## Success Criteria *(mandatory)*
  ### Measurable Outcomes
    - **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]

## Assumptions
  - [Assumption about target users / scope boundaries / data/environment / dependencies]
```

**Mandatory sections**: `User Scenarios & Testing`, `Requirements`, `Success Criteria` must be completed for every feature.
**Optional sections**: Include `Key Entities` only when relevant to the feature.
When a section doesn't apply, remove it entirely (don't leave as "N/A").

## Specification Quality Validation

After writing the initial spec, validate it against quality criteria:

a. **Create Spec Quality Checklist**: Generate a checklist file at `FEATURE_DIR/checklists/requirements.md` using the structure:

   ```markdown
   # Specification Quality Checklist: [FEATURE NAME]

   **Purpose**: Validate specification completeness and quality before proceeding to planning
   **Created**: [DATE]
   **Feature**: [Link to spec.md]

   ## Content Quality

   - [ ] No implementation details (languages, frameworks, APIs)
   - [ ] Focused on user value and business needs
   - [ ] Written for non-technical stakeholders
   - [ ] All mandatory sections completed

   ## Requirement Completeness

   - [ ] No [NEEDS CLARIFICATION] markers remain
   - [ ] Requirements are testable and unambiguous
   - [ ] Success criteria are measurable
   - [ ] Success criteria are technology-agnostic (no implementation details)
   - [ ] All acceptance scenarios are defined
   - [ ] Edge cases are identified
   - [ ] Scope is clearly bounded
   - [ ] Dependencies and assumptions identified

   ## Feature Readiness

   - [ ] All functional requirements have clear acceptance criteria
   - [ ] User scenarios cover primary flows
   - [ ] Feature meets measurable outcomes defined in Success Criteria
   - [ ] No implementation details leak into specification

   ## Notes

   - Items marked incomplete require spec updates before `sdd-clarify` or `sdd-plan`
   ```

b. **Run Validation Check**: Review the spec against each checklist item:
   - For each item, determine if it passes or fails.
   - Document specific issues found (quote relevant spec sections).

c. **Handle Validation Results**:

   - **If all items pass**: Mark checklist complete and proceed to the Completion Report.

   - **If items fail (excluding `[NEEDS CLARIFICATION]`)**:
     1. List the failing items and specific issues.
     2. Update the spec to address each issue.
     3. Re-run validation until all items pass (max 3 iterations).
     4. If still failing after 3 iterations, document remaining issues in checklist notes and warn the user.

   - **If `[NEEDS CLARIFICATION]` markers remain**:
     1. Extract all `[NEEDS CLARIFICATION: ...]` markers from the spec.
     2. **LIMIT CHECK**: If more than 3 markers exist, keep only the 3 most critical (by scope/security/UX impact) and make informed guesses for the rest.
     3. For each clarification needed (max 3), present options to the user in this format:

        ```markdown
        ## Question [N]: [Topic]

        **Context**: [Quote relevant spec section]

        **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

        **Suggested Answers**:

        | Option | Answer | Implications |
        |--------|--------|--------------|
        | A      | [First suggested answer] | [What this means for the feature] |
        | B      | [Second suggested answer] | [What this means for the feature] |
        | C      | [Third suggested answer] | [What this means for the feature] |
        | Custom | Provide your own answer | [Explain how to provide custom input] |

        **Your choice**: _[Wait for user response]_
        ```

     4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted with consistent spacing, spaces around content (`| Content |`), and header separators with at least 3 dashes.
     5. Number questions sequentially (Q1, Q2, Q3 — max 3 total).
     6. Present all questions together before waiting for responses.
     7. Wait for the user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B").
     8. Update the spec by replacing each `[NEEDS CLARIFICATION]` marker with the user's selected or provided answer.
     9. Re-run validation after all clarifications are resolved.

d. **Update Checklist**: After each validation iteration, update the checklist file with current pass/fail status.

## Completion Report

Report completion to the user with:
- `FEATURE_DIR` — the feature directory path
- `SPEC_FILE` — the spec file path
- Checklist results summary
- Readiness for the next phase

**Next**: invoke the `sdd-clarify` skill to resolve remaining ambiguities, or directly invoke the `sdd-plan` skill to build the technical plan.

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- DO NOT create any checklists embedded in the spec. The quality checklist is a separate file under `checklists/`.

### For AI Generation

When creating this spec from the user's feature description:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps.
2. **Document assumptions**: Record reasonable defaults in the Assumptions section.
3. **Limit clarifications**: Maximum 3 `[NEEDS CLARIFICATION]` markers — use only for critical decisions that:
   - Significantly impact feature scope or user experience.
   - Have multiple reasonable interpretations with different implications.
   - Lack any reasonable default.
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details.
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item.
6. **Common areas needing clarification** (only if no reasonable default exists):
   - Feature scope and boundaries (include/exclude specific use cases).
   - User types and permissions (if multiple conflicting interpretations possible).
   - Security/compliance requirements (when legally/financially significant).

**Examples of reasonable defaults** (don't ask about these):

- Data retention: Industry-standard practices for the domain.
- Performance targets: Standard web/mobile app expectations unless specified.
- Error handling: User-friendly messages with appropriate fallbacks.
- Authentication method: Standard session-based or OAuth2 for web apps.
- Integration patterns: Use project-appropriate patterns (REST/GraphQL for web services, function calls for libraries, CLI args for tools, etc.).

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate).
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools.
3. **User-focused**: Describe outcomes from user/business perspective, not system internals.
4. **Verifiable**: Can be tested/validated without knowing implementation details.

**Good examples**:
- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"

**Bad examples** (implementation-focused):
- "API response time is under 200ms" (too technical)
- "Database can handle 1000 TPS" (implementation detail)
- "React components render efficiently" (framework-specific)

## Done When

- [ ] Specification written to `SPEC_FILE` and validated against quality checklist.
- [ ] Git branch `<NNN>-<short-slug>` created.
- [ ] Completion reported to user with feature directory, spec file path, and checklist results.

---
_Ported from [GitHub Spec-Kit](https://github.com/github/spec-kit) `templates/commands/specify.md` (CC0/MIT). Licensed under MIT — see repository LICENSE. Logic preserved for DeepSeek Harness skill execution._