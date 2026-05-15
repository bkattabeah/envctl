"""Checkpoint: named save-points that capture target state at a logical milestone."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.env_store import EnvStore


def _checkpoint_dir(base: str) -> str:
    return os.path.join(base, ".checkpoints")


@dataclass
class CheckpointResult:
    target: str
    checkpoint_id: str
    label: Optional[str]
    env: Dict[str, str]
    created_at: float = field(default_factory=time.time)

    def summary(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return (
            f"Checkpoint {self.checkpoint_id}{label_part} saved for '{self.target}' "
            f"with {len(self.env)} key(s)."
        )


def create_checkpoint(
    store: EnvStore, target: str, label: Optional[str] = None
) -> CheckpointResult:
    env = store.load(target)
    ts = time.time()
    slug = label.lower().replace(" ", "-") if label else "cp"
    checkpoint_id = f"{target}-{slug}-{int(ts)}"

    cp_dir = _checkpoint_dir(store.base_dir)
    os.makedirs(cp_dir, exist_ok=True)

    record = {
        "target": target,
        "checkpoint_id": checkpoint_id,
        "label": label,
        "env": env,
        "created_at": ts,
    }
    path = os.path.join(cp_dir, f"{checkpoint_id}.json")
    with open(path, "w") as fh:
        json.dump(record, fh, indent=2)

    return CheckpointResult(
        target=target,
        checkpoint_id=checkpoint_id,
        label=label,
        env=env,
        created_at=ts,
    )


def list_checkpoints(base_dir: str, target: Optional[str] = None) -> List[CheckpointResult]:
    cp_dir = _checkpoint_dir(base_dir)
    if not os.path.isdir(cp_dir):
        return []
    results = []
    for fname in sorted(os.listdir(cp_dir)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(cp_dir, fname)) as fh:
            data = json.load(fh)
        if target and data["target"] != target:
            continue
        results.append(
            CheckpointResult(
                target=data["target"],
                checkpoint_id=data["checkpoint_id"],
                label=data.get("label"),
                env=data["env"],
                created_at=data["created_at"],
            )
        )
    return results


def load_checkpoint(base_dir: str, checkpoint_id: str) -> Optional[CheckpointResult]:
    path = os.path.join(_checkpoint_dir(base_dir), f"{checkpoint_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        data = json.load(fh)
    return CheckpointResult(
        target=data["target"],
        checkpoint_id=data["checkpoint_id"],
        label=data.get("label"),
        env=data["env"],
        created_at=data["created_at"],
    )


def delete_checkpoint(base_dir: str, checkpoint_id: str) -> bool:
    path = os.path.join(_checkpoint_dir(base_dir), f"{checkpoint_id}.json")
    if not os.path.exists(path):
        return False
    os.remove(path)
    return True
