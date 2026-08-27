"""Installer: copies bundled SDD assets into a project's .dsh tree."""

from __future__ import annotations

import shutil
from importlib.resources import files
from pathlib import Path

from .manifest import Manifest

SKILLS_DIR_RELPATH = ".dsh/skills"
TEMPLATES_DIR_RELPATH = ".dsh/sdd/templates"
AGENTS_DIR_RELPATH = ".dsh/sdd/agents"
CONSTITUTION_RELPATH = "memory/constitution.md"
SPECS_DIR_RELPATH = "specs"


def _package_root() -> Path:
    return Path(str(files("dsh_sdd")))


def _bundled(*parts: str) -> Path:
    return _package_root().joinpath(*parts)


def skills_available() -> list[str]:
    """Sorted list of bundled skill directory names."""
    skills_root = _bundled("skills")
    if not skills_root.is_dir():
        return []
    return sorted(
        d.name for d in skills_root.iterdir() if (d / "SKILL.md").is_file()
    )


def _write_bytes(manifest: Manifest, relpath: str, content: bytes) -> None:
    manifest.record(relpath, content)
    target = manifest.root / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)


def _copy_into(manifest: Manifest, src: Path, dest_relpath: str) -> None:
    _write_bytes(manifest, dest_relpath, src.read_bytes())


def install(root: Path, *, with_constitution: bool = True) -> Manifest:
    """Install all SDD assets into ``root``. Returns the saved manifest."""
    root = root.resolve()
    manifest = Manifest.load(root)

    # 1. Skills -> .dsh/skills/<name>/SKILL.md  (DSH project root, rank 100)
    for name in skills_available():
        src = _bundled("skills", name, "SKILL.md")
        _copy_into(manifest, src, f"{SKILLS_DIR_RELPATH}/{name}/SKILL.md")

    # 2. Templates -> .dsh/sdd/templates/*.md
    templates_root = _bundled("templates")
    if templates_root.is_dir():
        for f in sorted(templates_root.glob("*.md")):
            _copy_into(manifest, f, f"{TEMPLATES_DIR_RELPATH}/{f.name}")

    # 3. Subagent prompt definitions -> .dsh/sdd/agents/*.md
    agents_root = _bundled("agents")
    if agents_root.is_dir():
        for f in sorted(agents_root.glob("*.md")):
            _copy_into(manifest, f, f"{AGENTS_DIR_RELPATH}/{f.name}")

    # 4. Constitution -> memory/constitution.md (seed only if absent)
    if with_constitution:
        const_target = root / CONSTITUTION_RELPATH
        if const_target.exists():
            manifest.record_existing(CONSTITUTION_RELPATH)
        else:
            src = _bundled("templates", "constitution-template.md")
            _copy_into(manifest, src, CONSTITUTION_RELPATH)

    # 5. specs/ scaffold
    gitkeep = root / SPECS_DIR_RELPATH / ".gitkeep"
    if not gitkeep.exists():
        _write_bytes(manifest, f"{SPECS_DIR_RELPATH}/.gitkeep", b"")

    manifest.save()
    return manifest


def status(root: Path) -> dict[str, object]:
    """Report installed assets for ``root``."""
    root = root.resolve()
    manifest = Manifest.load(root)
    skills = [
        p.parent.name
        for p in sorted((root / SKILLS_DIR_RELPATH).glob("*/SKILL.md"))
    ]
    return {
        "root": str(root),
        "manifest": str(root / ".dsh/sdd/manifest.json"),
        "installed_files": len(manifest.files),
        "tracked": sorted(manifest.files),
        "skills": skills,
        "constitution": (root / CONSTITUTION_RELPATH).exists(),
    }
