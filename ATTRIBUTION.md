# Attribution

This project adapts **GitHub Spec-Kit** — <https://github.com/github/spec-kit> — a toolkit for Spec-Driven Development (SDD).

## What was reused

- The SDD methodology and workflow described in `spec-driven.md` and the command documentation.
- Command logic from `templates/commands/*.md` (`specify`, `plan`, `tasks`, `constitution`, `analyze`, `clarify`, `converge`, `implement`, `checklist`), ported to DeepSeek Harness `SKILL.md` skills under `src/dsh_sdd/skills/`.
- File templates `templates/{spec,plan,tasks,checklist}-template.md`, copied into this package's `templates/` directory.
- The hash-tracked install/uninstall manifest approach from Spec-Kit's `IntegrationManifest`, reimplemented in `src/dsh_sdd/manifest.py`.

## What was changed for DeepSeek Harness

- CLI-driven command files were ported to DSH **skills** (`SKILL.md`), discovered per-project from `.dsh/skills/` by DSH's `skill-filesystem` provider.
- Research, task execution, and consistency validation are delegated to DSH **subagents** (prompt definitions under `agents/`) rather than spawned CLI scripts.
- The constitution template was adapted for DSH's skill + subagent execution model.
- Spec-Kit's invocation placeholders (`$ARGUMENTS`, `{SCRIPT}`, `__SPECKIT_COMMAND_*__`, extension hooks) were removed; DSH skills receive input from the live conversation.

## License

Spec-Kit is distributed under the MIT License (see `LICENSE` in this repository and the Spec-Kit repository). Reused logic and templates remain under that license. New code in this repository is also MIT.
