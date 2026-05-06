"""Snapshot management: capture, list, restore, and compare env snapshots."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

SNAPSHOT_DIR = ".envctl_snapshots"


def _snapshot_dir(base: str = ".") -> Path:
    return Path(base) / SNAPSHOT_DIR


def create_snapshot(
    target: str,
    env: Dict[str, str],
    label: Optional[str] = None,
    base: str = ".",
) -> str:
    """Persist a snapshot for *target* and return the snapshot ID."""
    snap_dir = _snapshot_dir(base) / target
    snap_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snap_id = f"{ts}_{label}" if label else ts
    snap_file = snap_dir / f"{snap_id}.json"

    payload = {
        "target": target,
        "snapshot_id": snap_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": label,
        "env": env,
    }
    snap_file.write_text(json.dumps(payload, indent=2))
    return snap_id


def list_snapshots(target: str, base: str = ".") -> List[dict]:
    """Return snapshot metadata for *target*, newest first."""
    snap_dir = _snapshot_dir(base) / target
    if not snap_dir.exists():
        return []
    entries = []
    for f in sorted(snap_dir.glob("*.json"), reverse=True):
        data = json.loads(f.read_text())
        entries.append(
            {
                "snapshot_id": data["snapshot_id"],
                "created_at": data["created_at"],
                "label": data.get("label"),
                "keys": len(data["env"]),
            }
        )
    return entries


def load_snapshot(target: str, snapshot_id: str, base: str = ".") -> Dict[str, str]:
    """Load and return the env dict for a specific snapshot."""
    snap_file = _snapshot_dir(base) / target / f"{snapshot_id}.json"
    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_id}' not found for target '{target}'")
    return json.loads(snap_file.read_text())["env"]


def delete_snapshot(target: str, snapshot_id: str, base: str = ".") -> None:
    """Remove a single snapshot file."""
    snap_file = _snapshot_dir(base) / target / f"{snapshot_id}.json"
    if not snap_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_id}' not found for target '{target}'")
    snap_file.unlink()
