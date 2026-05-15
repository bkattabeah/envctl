"""Pipeline: chain multiple env operations and apply them sequentially to a target."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from envctl.env_store import EnvStore


@dataclass
class PipelineStep:
    name: str
    fn: Callable[[Dict[str, str]], Dict[str, str]]


@dataclass
class PipelineResult:
    target: str
    steps_applied: List[str]
    initial_env: Dict[str, str]
    final_env: Dict[str, str]
    skipped: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def summary(self) -> str:
        if self.error:
            return f"Pipeline failed on '{self.target}': {self.error}"
        applied = len(self.steps_applied)
        skipped = len(self.skipped)
        changed = sum(
            1 for k in self.final_env
            if self.final_env.get(k) != self.initial_env.get(k)
        ) + sum(1 for k in self.initial_env if k not in self.final_env)
        parts = [f"{applied} step(s) applied", f"{changed} key(s) changed"]
        if skipped:
            parts.append(f"{skipped} step(s) skipped")
        return f"Pipeline '{self.target}': " + ", ".join(parts) + "."


def run_pipeline(
    store: EnvStore,
    target: str,
    steps: List[PipelineStep],
    *,
    dry_run: bool = False,
) -> PipelineResult:
    """Apply a sequence of transformation steps to a target's environment."""
    env = store.load(target)
    if env is None:
        return PipelineResult(
            target=target,
            steps_applied=[],
            initial_env={},
            final_env={},
            error=f"Target '{target}' not found.",
        )

    initial_env = dict(env)
    current = dict(env)
    applied: List[str] = []
    skipped: List[str] = []

    for step in steps:
        try:
            result = step.fn(dict(current))
            if not isinstance(result, dict):
                raise TypeError("Step must return a dict.")
            current = result
            applied.append(step.name)
        except Exception as exc:  # noqa: BLE001
            skipped.append(step.name)
            continue

    if not dry_run:
        store.save(target, current)

    return PipelineResult(
        target=target,
        steps_applied=applied,
        initial_env=initial_env,
        final_env=current,
        skipped=skipped,
    )
