"""Score a target environment against a set of quality heuristics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envctl.env_store import EnvStore
from envctl.lint import lint_target
from envctl.validate import validate_target


@dataclass
class ScoreResult:
    target: str
    total_keys: int
    lint_errors: int
    lint_warnings: int
    validation_errors: int
    validation_warnings: int
    missing_values: int  # keys present but empty
    duplicate_prefixes: int  # keys sharing the same prefix group
    breakdown: Dict[str, int] = field(default_factory=dict)

    # Maximum achievable points per category
    _MAX = 100

    @property
    def score(self) -> int:
        """Return an integer quality score 0-100."""
        deductions = (
            self.lint_errors * 10
            + self.lint_warnings * 3
            + self.validation_errors * 8
            + self.validation_warnings * 2
            + self.missing_values * 5
            + self.duplicate_prefixes * 1
        )
        return max(0, self._MAX - deductions)

    @property
    def grade(self) -> str:
        s = self.score
        if s >= 90:
            return "A"
        if s >= 75:
            return "B"
        if s >= 60:
            return "C"
        if s >= 40:
            return "D"
        return "F"

    def summary(self) -> str:
        return (
            f"{self.target}: score={self.score}/100 grade={self.grade} "
            f"keys={self.total_keys} lint_err={self.lint_errors} "
            f"val_err={self.validation_errors} empty={self.missing_values}"
        )


def _count_duplicate_prefixes(env: Dict[str, str]) -> int:
    """Count keys whose prefix (up to first '_') appears more than once."""
    from collections import Counter
    prefixes = [k.split("_")[0] for k in env if "_" in k]
    return sum(1 for cnt in Counter(prefixes).values() if cnt > 1)


def score_target(store: EnvStore, target: str) -> ScoreResult:
    env = store.load(target)
    lint_result = lint_target(env)
    val_result = validate_target(env)

    missing = sum(1 for v in env.values() if v.strip() == "")
    dup_prefixes = _count_duplicate_prefixes(env)

    breakdown = {
        "lint_errors": len(lint_result.errors()),
        "lint_warnings": len(lint_result.warnings()),
        "validation_errors": len(val_result.errors()),
        "validation_warnings": len(val_result.warnings()),
        "missing_values": missing,
        "duplicate_prefixes": dup_prefixes,
    }

    return ScoreResult(
        target=target,
        total_keys=len(env),
        lint_errors=len(lint_result.errors()),
        lint_warnings=len(lint_result.warnings()),
        validation_errors=len(val_result.errors()),
        validation_warnings=len(val_result.warnings()),
        missing_values=missing,
        duplicate_prefixes=dup_prefixes,
        breakdown=breakdown,
    )
