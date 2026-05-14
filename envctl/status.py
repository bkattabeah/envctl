"""Compute a high-level status summary for one or more targets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.env_store import EnvStore
from envctl.freeze import is_frozen
from envctl.validate import validate_env
from envctl.lint import lint_env


@dataclass
class TargetStatus:
    target: str
    key_count: int
    frozen: bool
    valid: bool
    lint_errors: int
    lint_warnings: int
    tags: List[str] = field(default_factory=list)

    @property
    def health(self) -> str:
        """Return a single-word health label."""
        if not self.valid or self.lint_errors > 0:
            return "error"
        if self.lint_warnings > 0:
            return "warn"
        return "ok"


@dataclass
class StatusResult:
    statuses: List[TargetStatus] = field(default_factory=list)

    def for_target(self, target: str) -> Optional[TargetStatus]:
        for s in self.statuses:
            if s.target == target:
                return s
        return None

    @property
    def summary(self) -> str:
        total = len(self.statuses)
        errors = sum(1 for s in self.statuses if s.health == "error")
        warns = sum(1 for s in self.statuses if s.health == "warn")
        ok = total - errors - warns
        parts = [f"{total} target(s)"]
        if ok:
            parts.append(f"{ok} ok")
        if warns:
            parts.append(f"{warns} warn")
        if errors:
            parts.append(f"{errors} error")
        return " | ".join(parts)


def status_targets(
    store: EnvStore,
    targets: Optional[List[str]] = None,
    *,
    base_dir: str = ".",
) -> StatusResult:
    """Collect status for each target (all targets if *targets* is None)."""
    names = targets if targets is not None else store.list_targets()
    result = StatusResult()

    for name in names:
        env = store.load(name)
        frozen = is_frozen(name, base_dir=base_dir)

        val_result = validate_env(env)
        lint_result = lint_env(env)

        # tags — best-effort; ignore if tag module unavailable
        try:
            from envctl.tag import load_tags
            tags = load_tags(name, base_dir=base_dir)
        except Exception:
            tags = []

        result.statuses.append(
            TargetStatus(
                target=name,
                key_count=len(env),
                frozen=frozen,
                valid=val_result.is_valid,
                lint_errors=len(lint_result.errors),
                lint_warnings=len(lint_result.warnings),
                tags=tags,
            )
        )

    return result
