"""Archive and restore environment targets as compressed bundles."""

from __future__ import annotations

import json
import zipfile
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envctl.env_store import EnvStore


@dataclass
class ArchiveResult:
    target: str
    archive_path: str
    keys_archived: List[str] = field(default_factory=list)
    restored_to: Optional[str] = None
    overwritten_keys: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.restored_to:
            parts = [f"Restored '{self.target}' → '{self.restored_to}' ({len(self.keys_archived)} keys)"]
            if self.overwritten_keys:
                parts.append(f"overwritten: {', '.join(sorted(self.overwritten_keys))}")
            return "; ".join(parts)
        return (
            f"Archived '{self.target}' → {self.archive_path} "
            f"({len(self.keys_archived)} keys)"
        )


def archive_target(
    store: EnvStore,
    target: str,
    dest_dir: str,
) -> ArchiveResult:
    """Write a target's env vars to a .zip archive bundle."""
    env = store.load(target)
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    archive_path = dest / f"{target}.envbundle"

    payload = json.dumps(env, indent=2, sort_keys=True).encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{target}.json", payload)
    archive_path.write_bytes(buf.getvalue())

    return ArchiveResult(
        target=target,
        archive_path=str(archive_path),
        keys_archived=sorted(env.keys()),
    )


def restore_archive(
    store: EnvStore,
    archive_path: str,
    dest_target: str,
    overwrite: bool = False,
) -> ArchiveResult:
    """Restore env vars from a .envbundle archive into a target."""
    path = Path(archive_path)
    with zipfile.ZipFile(path, mode="r") as zf:
        name = zf.namelist()[0]
        env: dict = json.loads(zf.read(name).decode())

    existing = store.load(dest_target) if dest_target in store.list_targets() else {}
    overwritten: List[str] = []
    merged = dict(existing)
    for k, v in env.items():
        if k in merged:
            if overwrite:
                overwritten.append(k)
                merged[k] = v
        else:
            merged[k] = v

    store.save(dest_target, merged)
    source_target = path.stem
    return ArchiveResult(
        target=source_target,
        archive_path=str(path),
        keys_archived=sorted(env.keys()),
        restored_to=dest_target,
        overwritten_keys=overwritten,
    )
