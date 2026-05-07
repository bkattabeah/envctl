"""Pin specific environment variable keys to required values for a target."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


def _pin_path(base_dir: str, target: str) -> Path:
    return Path(base_dir) / target / "pins.json"


def save_pins(base_dir: str, target: str, pins: Dict[str, str]) -> None:
    path = _pin_path(base_dir, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(pins, f, sort_keys=True, indent=2)


def load_pins(base_dir: str, target: str) -> Dict[str, str]:
    path = _pin_path(base_dir, target)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def add_pin(base_dir: str, target: str, key: str, value: str) -> None:
    pins = load_pins(base_dir, target)
    pins[key] = value
    save_pins(base_dir, target, pins)


def remove_pin(base_dir: str, target: str, key: str) -> bool:
    pins = load_pins(base_dir, target)
    if key not in pins:
        return False
    del pins[key]
    save_pins(base_dir, target, pins)
    return True


@dataclass
class PinViolation:
    key: str
    expected: str
    actual: Optional[str]

    def __str__(self) -> str:
        actual_display = repr(self.actual) if self.actual is not None else "<missing>"
        return f"{self.key}: expected {repr(self.expected)}, got {actual_display}"


@dataclass
class PinCheckResult:
    target: str
    violations: List[PinViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def summary(self) -> str:
        if self.passed:
            return f"[{self.target}] All pins satisfied."
        lines = [f"[{self.target}] {len(self.violations)} pin violation(s):"]
        for v in self.violations:
            lines.append(f"  - {v}")
        return "\n".join(lines)


def check_pins(base_dir: str, target: str, env: Dict[str, str]) -> PinCheckResult:
    pins = load_pins(base_dir, target)
    violations = []
    for key, expected in sorted(pins.items()):
        actual = env.get(key)
        if actual != expected:
            violations.append(PinViolation(key=key, expected=expected, actual=actual))
    return PinCheckResult(target=target, violations=violations)
