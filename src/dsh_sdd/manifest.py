"""Hash-tracked install manifest for the dsh-sdd CLI.

Mirrors GitHub Spec-Kit's ``IntegrationManifest`` semantics: every file the
installer writes is recorded with its SHA-256 hash so that ``uninstall`` can
remove only files that are still byte-identical to what we installed, skipping
files the user edited by hand (unless ``force=True``).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

MANIFEST_PATH = ".dsh/sdd/manifest.json"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256(path.read_bytes())


@dataclass
class Manifest:
    """Records installed files (project-relative) and their content hashes."""

    root: Path
    files: dict[str, str] = field(default_factory=dict)  # rel path -> sha256

    @property
    def manifest_file(self) -> Path:
        return self.root / MANIFEST_PATH

    @classmethod
    def load(cls, root: Path) -> "Manifest":
        mf = root / MANIFEST_PATH
        if not mf.exists():
            return cls(root=root)
        data = json.loads(mf.read_text(encoding="utf-8"))
        return cls(root=root, files=dict(data.get("files", {})))

    def record(self, relpath: str, content: bytes) -> None:
        """Record a file we are about to write, with its content hash."""
        self.files[relpath] = _sha256(content)

    def record_existing(self, relpath: str) -> None:
        """Adopt a pre-existing file into the manifest using its current hash."""
        self.files[relpath] = _sha256_file(self.root / relpath)

    def save(self) -> None:
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "tool": "dsh-sdd",
            "files": dict(sorted(self.files.items())),
        }
        self.manifest_file.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )

    def _still_ours(self, relpath: str) -> bool:
        target = self.root / relpath
        if not target.exists():
            return False
        recorded = self.files.get(relpath)
        if recorded is None:
            return False
        return _sha256_file(target) == recorded

    def uninstall(self, force: bool = False) -> tuple[list[str], list[str]]:
        """Remove tracked files.

        Returns (removed, skipped). Files the user modified since install are
        skipped unless ``force`` is set. Empty parent directories under
        ``.dsh/`` are cleaned up.
        """
        removed: list[str] = []
        skipped: list[str] = []
        for relpath in sorted(self.files, key=lambda p: p.count("/"), reverse=True):
            target = self.root / relpath
            if not target.exists():
                continue
            if force or self._still_ours(relpath):
                target.unlink()
                removed.append(relpath)
            else:
                skipped.append(relpath)
        self.files.clear()
        # Remove the manifest itself (always ours).
        if self.manifest_file.exists():
            self.manifest_file.unlink()
        self._prune_empty_dirs()
        return removed, skipped

    def _prune_empty_dirs(self) -> None:
        anchor = self.root / ".dsh"
        if not anchor.exists():
            return
        for d in sorted(
            (p for p in anchor.rglob("*") if p.is_dir()),
            key=lambda p: len(p.parts),
            reverse=True,
        ):
            try:
                d.rmdir()
            except OSError:
                pass
        # Do not remove the .dsh root itself if it now holds nothing else the
        # user may rely on; only remove if it is empty.
        try:
            anchor.rmdir()
        except OSError:
            pass
