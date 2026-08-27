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

### The 11 skills

| Skill | Step | Produces |
|---|---|---|
| `sdd-runner` | Drive the whole cycle as a goal | orchestrated specify→plan→tasks→implement→analyze, wave dispatch |
| `sdd-guardian` | Constitution coverage at intake | coverage table + amendments BEFORE ungoverned work starts |
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

## Goal-driven cycle (orchestrated)

`sdd-runner` turns one feature description into an autonomous run: it creates a **DSH goal** (same-session, resumable across rounds via the `/goal` command/goal tools), drives the SDD skills in order, pauses at spec/plan review gates for approval, then dispatches implementation in **parallel waves of implementer subagents** (disjoint file ownership, test-first), each wave gated by an **independent reviewer subagent**. State persists in `specs/<NNN-slug>/cycle-state.json` so interrupted runs resume.

Kick it off by describing a goal, e.g. *"Run the SDD cycle for: real-time notifications per user"*. The role prompts live in `.dsh/sdd/agents/` — `implementer.md` (test-first unit implementer) and `implementation-reviewer.md` (independent wave gatekeeper), alongside `research-agent.md`, `task-agent.md`, `consistency-agent.md`.


## Install

Requires **Python ≥ 3.11** and `pip`. [`uv`](https://docs.astral.sh/uv/) is the recommended installer.

```bash
# Option A — one-shot with uv (isolated env created and managed for you):
uv tool install "git+https://github.com/krokrolabs/spec-kit-deepseek-harness.git"

# Option B — inside your own venv (uv or pip); the public repo needs no SSH key:
uv pip install "git+https://github.com/krokrolabs/spec-kit-deepseek-harness.git"
# or:
pip install "git+https://github.com/krokrolabs/spec-kit-deepseek-harness.git"

# Option C — from a local checkout:
pip install .   # or: uv pip install .

# Then, inside a git repo (project root detected via .git):
cd /path/to/your-project
dsh-sdd init
```

With `uv tool install` the `dsh-sdd` command is on your PATH with no venv to
activate. Upgrade later with `uv tool upgrade dsh-sdd`; remove it with
`uv tool uninstall dsh-sdd`.

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

## Releases & updating

Stable installs pin a release tag — reproducible and isolated from `main`:

```bash
uv tool install "git+https://github.com/krokrolabs/spec-kit-deepseek-harness.git@v0.2.0"
```

To move a project to a newer release:

```bash
uv tool install --force "git+https://github.com/krokrolabs/spec-kit-deepseek-harness.git@v<new>" # refresh the CLI
dsh-sdd install                    # refresh the project's skills/templates/agents
```

`dsh-sdd install` overwrites bundled assets with the new versions and re-records the manifest; files you hand-edited are **not** touched (they keep their content and are skipped on uninstall). Releases and tags live at [github.com/krokrolabs/spec-kit-deepseek-harness/releases](https://github.com/krokrolabs/spec-kit-deepseek-harness/releases).

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
