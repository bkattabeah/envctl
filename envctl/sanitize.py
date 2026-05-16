"""Sanitize environment variable sets by normalizing keys and values."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class SanitizeResult:
    target: str
    original: Dict[str, str]
    sanitized: Dict[str, str]
    renamed: Dict[str, str]   # old_key -> new_key
    stripped: List[str]       # keys whose values were whitespace-stripped
    removed: List[str]        # keys removed (empty value after strip)

    def summary(self) -> str:
        parts = []
        if self.renamed:
            parts.append(f"{len(self.renamed)} key(s) renamed")
        if self.stripped:
            parts.append(f"{len(self.stripped)} value(s) stripped")
        if self.removed:
            parts.append(f"{len(self.removed)} empty key(s) removed")
        if not parts:
            return f"[{self.target}] already clean — no changes made"
        return f"[{self.target}] sanitized: " + ", ".join(parts)


def _normalize_key(key: str) -> str:
    """Uppercase and replace non-alphanumeric characters with underscores."""
    normalized = re.sub(r"[^A-Z0-9_]", "_", key.upper())
    # Collapse multiple underscores
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized


def sanitize_target(
    store,
    target: str,
    remove_empty: bool = True,
    normalize_keys: bool = True,
    dry_run: bool = False,
) -> SanitizeResult:
    """Sanitize the environment for *target*.

    Args:
        store: EnvStore instance.
        target: Target name to sanitize.
        remove_empty: Drop keys whose value is empty after stripping.
        normalize_keys: Uppercase keys and replace invalid chars with '_'.
        dry_run: Compute result but do not persist changes.

    Returns:
        SanitizeResult describing all mutations.
    """
    original: Dict[str, str] = store.load(target)
    sanitized: Dict[str, str] = {}
    renamed: Dict[str, str] = {}
    stripped: List[str] = []
    removed: List[str] = []

    for key, value in original.items():
        # Strip whitespace from value
        clean_value = value.strip()
        if clean_value != value:
            stripped.append(key)

        # Remove empty values if requested
        if remove_empty and clean_value == "":
            removed.append(key)
            continue

        # Normalize key if requested
        new_key = _normalize_key(key) if normalize_keys else key
        if new_key != key:
            renamed[key] = new_key

        sanitized[new_key] = clean_value

    result = SanitizeResult(
        target=target,
        original=original,
        sanitized=sanitized,
        renamed=renamed,
        stripped=[k for k in stripped if k not in removed],
        removed=removed,
    )

    if not dry_run:
        store.save(target, sanitized)

    return result
