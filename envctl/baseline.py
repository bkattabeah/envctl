"""Baseline management: mark a target's current state as a reference point."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envctl.env_store import EnvStore


def _baseline_dir(base: Path) -> Path:
    return base / ".envctl" / "baselines"


@dataclass
class BaselineResult:
    target: str
    baseline_id: str
    env: dict[str, str]
    created_at: float = field(default_factory=time.time)
    label: Optional[str] = None

    def summary(self) -> str:
        tag = f" [{self.label}]" if self.label else ""
        return (
            f"Baseline '{self.baseline_id}'{tag} saved for target '{self.target}' "
            f"({len(self.env)} keys)."
        )


def set_baseline(
    store: EnvStore,
    target: str,
    label: Optional[str] = None,
) -> BaselineResult:
    """Capture the current state of *target* as a named baseline."""
    env = store.load(target)
    ts = time.time()
    slug = label.replace(" ", "-") if label else "baseline"
    baseline_id = f"{target}__{slug}__{int(ts)}"

    baseline_dir = _baseline_dir(store.base_path)
    baseline_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "target": target,
        "baseline_id": baseline_id,
        "label": label,
        "created_at": ts,
        "env": env,
    }
    (baseline_dir / f"{baseline_id}.json").write_text(
        json.dumps(record, indent=2, sort_keys=True)
    )
    return BaselineResult(
        target=target, baseline_id=baseline_id, env=env, created_at=ts, label=label
    )


def load_baseline(base: Path, baseline_id: str) -> BaselineResult:
    path = _baseline_dir(base) / f"{baseline_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Baseline not found: {baseline_id}")
    data = json.loads(path.read_text())
    return BaselineResult(
        target=data["target"],
        baseline_id=data["baseline_id"],
        env=data["env"],
        created_at=data["created_at"],
        label=data.get("label"),
    )


def list_baselines(base: Path, target: Optional[str] = None) -> list[BaselineResult]:
    d = _baseline_dir(base)
    if not d.exists():
        return []
    results = []
    for p in sorted(d.glob("*.json")):
        data = json.loads(p.read_text())
        if target and data["target"] != target:
            continue
        results.append(
            BaselineResult(
                target=data["target"],
                baseline_id=data["baseline_id"],
                env=data["env"],
                created_at=data["created_at"],
                label=data.get("label"),
            )
        )
    return results


def delete_baseline(base: Path, baseline_id: str) -> bool:
    path = _baseline_dir(base) / f"{baseline_id}.json"
    if not path.exists():
        return False
    path.unlink()
    return True
