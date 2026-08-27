"""Tests for the dsh-sdd installer and manifest."""

from __future__ import annotations

from pathlib import Path

import pytest

from dsh_sdd.cli import find_project_root, main
from dsh_sdd.installer import install, skills_available, status
from dsh_sdd.manifest import Manifest

SKILL_NAMES = {
    "sdd-specify",
    "sdd-plan",
    "sdd-tasks",
    "sdd-constitution",
    "sdd-analyze",
    "sdd-clarify",
    "sdd-converge",
    "sdd-implement",
    "sdd-checklist",
}


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    return tmp_path


def test_bundled_skills_present() -> None:
    assert set(skills_available()) == SKILL_NAMES


def test_find_project_root(repo: Path) -> None:
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    assert find_project_root(nested) == repo


def test_find_project_root_without_git(tmp_path: Path) -> None:
    assert find_project_root(tmp_path) == tmp_path


def test_install_scaffolds_everything(repo: Path) -> None:
    manifest = install(repo)
    # Skills installed
    for name in SKILL_NAMES:
        skill = repo / ".dsh" / "skills" / name / "SKILL.md"
        assert skill.is_file(), name
        head = skill.read_text(encoding="utf-8").splitlines()
        assert head[0] == "---" and head[1].strip() == f"name: {name}"
    # Templates, agents, constitution, specs
    assert (repo / ".dsh" / "sdd" / "templates" / "spec-template.md").is_file()
    assert (repo / ".dsh" / "sdd" / "agents" / "research-agent.md").is_file()
    assert (repo / "memory" / "constitution.md").is_file()
    assert (repo / "specs" / ".gitkeep").is_file()
    # Manifest saved and records files
    assert (repo / ".dsh" / "sdd" / "manifest.json").is_file()
    assert len(manifest.files) > 0


def test_status_reports_skills(repo: Path) -> None:
    install(repo)
    info = status(repo)
    assert set(info["skills"]) == SKILL_NAMES
    assert info["constitution"] is True
    assert info["installed_files"] == len(info["tracked"]) > 0


def test_uninstall_removes_unmodified(repo: Path) -> None:
    install(repo)
    manifest = Manifest.load(repo)
    removed, skipped = manifest.uninstall()
    assert not (repo / ".dsh").exists() or not list((repo / ".dsh").rglob("*.md"))
    assert skipped == []
    assert len(removed) > 0


def test_uninstall_skips_user_modified(repo: Path) -> None:
    install(repo)
    # Simulate a hand-edited skill file.
    edited = repo / ".dsh" / "skills" / "sdd-specify" / "SKILL.md"
    edited.write_text("user edited", encoding="utf-8")
    manifest = Manifest.load(repo)
    removed, skipped = manifest.uninstall()
    assert edited.is_file()  # not removed
    assert any("sdd-specify" in s for s in skipped)


def test_uninstall_force_removes_modified(repo: Path) -> None:
    install(repo)
    edited = repo / ".dsh" / "skills" / "sdd-plan" / "SKILL.md"
    edited.write_text("user edited", encoding="utf-8")
    manifest = Manifest.load(repo)
    manifest.uninstall(force=True)
    assert not edited.exists()


def test_reinstall_does_not_overwrite_edited_constitution(repo: Path) -> None:
    install(repo)
    constdir = repo / "memory" / "constitution.md"
    constdir.write_text("custom constitution", encoding="utf-8")
    install(repo)  # re-install adopts existing constitution, does not clobber
    assert constdir.read_text(encoding="utf-8") == "custom constitution"


def test_cli_init_and_list(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["init", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "installed SDD into" in out
    assert main(["list", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "sdd-specify" in out
