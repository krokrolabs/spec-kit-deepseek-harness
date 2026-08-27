# dsh-sdd — Spec-Driven Development for DeepSeek Harness

Brings [GitHub Spec-Kit](https://github.com/github/spec-kit)'s Spec-Driven Development (SDD) to **DeepSeek Harness** as project-local **skills** and runtime **subagents**. Specifications become the source of truth; code is regenerated from them.

> This is a port of Spec-Kit for DSH. See `ATTRIBUTION.md` for provenance and license.

## What SDD gives you

- **Specification-first** — every feature starts as `specs/<NNN-slug>/spec.md` (WHAT/WHY, not HOW).
- **Plans that trace to specs** — `plan.md` maps every technical choice to a requirement.
- **Research before building** — a research subagent writes `research.md`.
- **Executable task lists** — `tasks.md` with parallelization markers.
- **Continuous consistency** — an analysis pass checks spec/plan/tasks against a constitution.
- **Test-first implementation** — task subagents implement with failing tests first.

## How it works on DeepSeek Harness

SDD is installed into a project as **skills** in `.dsh/skills/<name>/SKILL.md`. DSH's `skill-filesystem` provider discovers them automatically (per-project; they hot-reload). Long or parallelizable work is spawned as **subagents** (`research`, `task`, `consistency`) from those skills. No global installs, no custom plugins.

### The 9 skills

| Skill | Step | Produces |
|---|---|---|
| `sdd-constitution` | Set up governance | `memory/constitution.md` |
| `sdd-specify` | Specify a feature | `specs/<NNN-slug>/spec.md` + branch |
| `sdd-clarify` | Resolve ambiguities | updated `spec.md` |
| `sdd-plan` | Plan the feature | `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` |
| `sdd-tasks` | Break into tasks | `tasks.md` |
| `sdd-analyze` | Consistency + gate check | findings report |
| `sdd-implement` | Build it (test-first) | working code + checked-off tasks |
| `sdd-converge` | Close spec/code gaps | appended `tasks.md` |
| `sdd-checklist` | Requirements quality | `checklists/<domain>.md` |

You don't have to type commands — say things like *"spec out user auth"*, *"plan the spec"*, *"break it into tasks"* and DSH surfaces the matching skill.

## Install

Requires **Python ≥ 3.11** and `pip`.

```bash
# Option A — no clone, straight from GitHub:
pip install "git+ssh://git@github.com/rafael-ariascalles/spec-kit-deepseek-harness.git"

# Option B — from a local checkout:
pip install .

# Then, inside a git repo (project root detected via .git):
cd /path/to/your-project
dsh-sdd init
```

Verify the install:

```bash
dsh-sdd list   # should show 9 sdd-* skills, templates, agents, and constitution: present
```

`init` scaffolds:

```
your-project/
├── .dsh/skills/sdd-*/SKILL.md     # discovered by DSH
├── .dsh/sdd/templates/*.md        # spec/plan/tasks/checklist templates
├── .dsh/sdd/agents/*.md           # research/task/consistency subagent prompts
├── memory/constitution.md         # project constitution
└── specs/                         # feature specs land here
```

Reload or restart DSH so the new skills are picked up, then start a feature: *"spec out a real-time chat feature"*.

### Other commands

```bash
dsh-sdd list              # show installed skills and asset status
dsh-sdd install           # (re)install assets
dsh-sdd uninstall         # remove only unmodified installed files
dsh-sdd uninstall --force # remove even user-modified files
```

Install is **manifest-tracked**: uninstall removes only files byte-identical to what was installed, skipping anything you edited by hand.

## The workflow

```text
specify → clarify → plan → tasks → analyze → implement → (converge)
```

1. **Specify** the feature → `spec.md`.
2. **Clarify** remaining ambiguities.
3. **Plan** → `plan.md` + research (subagent) + contracts + data model.
4. **Tasks** → `tasks.md`.
5. **Analyze** for constitution compliance and cross-artifact consistency.
6. **Implement** via test-first task subagents.

The constitution at `memory/constitution.md` enforces test-first, integration-first testing, simplicity, and anti-abstraction gates across every step.

## Requirements

- A project that is a git repository (`.git` marks the project root).
- DSH with the filesystem skill provider enabled (default `standard`/`code` presets).
- Python ≥ 3.11 for the installer CLI.

## License

MIT — see `LICENSE`. Adapted from GitHub Spec-Kit (MIT/CC0); see `ATTRIBUTION.md`.
