"""dsh-sdd command line interface.

Installs Spec-Driven Development assets (skills, templates, constitution,
subagent prompts) into a *project* so DeepSeek Harness discovers them.

Discovery: DSH's ``skill-filesystem`` provider scans ``<repoRoot>/.dsh/skills``
(highest precedence) and ``<repoRoot>/.agents/skills`` for ``<name>/SKILL.md``
directory bundles. We install into ``.dsh/skills`` (per-project; never global).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .installer import install, status
from .manifest import Manifest


def find_project_root(start: Path) -> Path:
    """Walk up from ``start`` until a ``.git`` directory is found."""
    current = start.resolve()
    while True:
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            # No .git found: use the starting directory as the project root.
            return start.resolve()
        current = parent


def _project_root(args: argparse.Namespace) -> Path:
    start = Path(args.path).resolve() if getattr(args, "path", None) else Path.cwd()
    return find_project_root(start)


def cmd_init(args: argparse.Namespace) -> int:
    root = _project_root(args)
    manifest = install(root, with_constitution=not args.no_constitution)
    print(f"dsh-sdd {__version__}: installed SDD into {root}")
    print(f"  skills:      {root}/.dsh/skills/ ({len(manifest.files)} files tracked)")
    print(f"  templates:   {root}/.dsh/sdd/templates/")
    print(f"  agents:      {root}/.dsh/sdd/agents/")
    print(f"  constitution:{root}/memory/constitution.md")
    print(f"  specs:       {root}/specs/")
    print("\nRestart or reload DSH (skills hot-reload) then say e.g. 'spec out <feature>'.")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    root = _project_root(args)
    install(root, with_constitution=not args.no_constitution)
    print(f"Installed SDD assets into {root}")
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    root = _project_root(args)
    manifest = Manifest.load(root)
    if not manifest.files:
        print(f"Nothing to uninstall under {root}")
        return 0
    removed, skipped = manifest.uninstall(force=args.force)
    print(f"Removed {len(removed)} files from {root}")
    if skipped:
        print("Skipped (modified since install; use --force to remove):")
        for rel in skipped:
            print(f"  {rel}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    root = _project_root(args)
    info = status(root)
    print(f"Root:          {info['root']}")
    print(f"Manifest:      {info['manifest']}")
    print(f"Files tracked: {info['installed_files']}")
    print(f"Constitution:  {'present' if info['constitution'] else 'absent'}")
    skills = info["skills"]
    print("Skills:")
    if skills:
        for name in skills:  # type: ignore[union-attr]
            print(f"  {name}")
    else:
        print("  (none installed)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dsh-sdd",
        description="Install Spec-Driven Development into a DeepSeek Harness project.",
    )
    parser.add_argument("--version", action="version", version=f"dsh-sdd {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_path(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "path",
            nargs="?",
            default=str(Path.cwd()),
            help="Project root (or any path inside it). Defaults to cwd.",
        )

    p_init = sub.add_parser("init", help="Scaffold skills, templates, constitution, specs.")
    add_path(p_init)
    p_init.add_argument("--no-constitution", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_install = sub.add_parser("install", help="(Re)install skills and assets.")
    add_path(p_install)
    p_install.add_argument("--no-constitution", action="store_true")
    p_install.set_defaults(func=cmd_install)

    p_uninstall = sub.add_parser("uninstall", help="Remove installed assets.")
    add_path(p_uninstall)
    p_uninstall.add_argument("--force", action="store_true", help="Remove even user-modified files.")
    p_uninstall.set_defaults(func=cmd_uninstall)

    p_list = sub.add_parser("list", help="Show installed skills and assets.")
    add_path(p_list)
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
