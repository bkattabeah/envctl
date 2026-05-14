"""Schema validation for environment variable sets.

Allows defining expected keys, types, and constraints for a target,
then validating a loaded env against that schema.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SchemaField:
    key: str
    required: bool = True
    pattern: str | None = None  # regex pattern the value must match
    allowed_values: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class SchemaResult:
    target: str
    missing_required: list[str] = field(default_factory=list)
    pattern_violations: dict[str, str] = field(default_factory=dict)  # key -> value
    disallowed_values: dict[str, str] = field(default_factory=dict)   # key -> value
    unknown_keys: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not (
            self.missing_required
            or self.pattern_violations
            or self.disallowed_values
        )

    def summary(self) -> str:
        if self.is_valid:
            return f"[{self.target}] schema OK"
        parts = []
        if self.missing_required:
            parts.append(f"{len(self.missing_required)} missing required key(s)")
        if self.pattern_violations:
            parts.append(f"{len(self.pattern_violations)} pattern violation(s)")
        if self.disallowed_values:
            parts.append(f"{len(self.disallowed_values)} disallowed value(s)")
        return f"[{self.target}] schema FAILED: " + ", ".join(parts)


def _schema_path(base_dir: str, schema_name: str) -> str:
    return os.path.join(base_dir, "schemas", f"{schema_name}.json")


def save_schema(base_dir: str, schema_name: str, fields: list[SchemaField]) -> None:
    path = _schema_path(base_dir, schema_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = [
        {
            "key": f.key,
            "required": f.required,
            "pattern": f.pattern,
            "allowed_values": f.allowed_values,
            "description": f.description,
        }
        for f in fields
    ]
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def load_schema(base_dir: str, schema_name: str) -> list[SchemaField]:
    path = _schema_path(base_dir, schema_name)
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        data = json.load(fh)
    return [
        SchemaField(
            key=item["key"],
            required=item.get("required", True),
            pattern=item.get("pattern"),
            allowed_values=item.get("allowed_values", []),
            description=item.get("description", ""),
        )
        for item in data
    ]


def validate_schema(
    target: str,
    env: dict[str, str],
    fields: list[SchemaField],
    strict: bool = False,
) -> SchemaResult:
    """Validate *env* against *fields*.

    When *strict* is True, keys present in the env but absent from the
    schema are recorded as unknown_keys.
    """
    import re

    result = SchemaResult(target=target)
    schema_keys = {f.key for f in fields}

    for f in fields:
        value = env.get(f.key)
        if value is None:
            if f.required:
                result.missing_required.append(f.key)
            continue
        if f.pattern and not re.fullmatch(f.pattern, value):
            result.pattern_violations[f.key] = value
        if f.allowed_values and value not in f.allowed_values:
            result.disallowed_values[f.key] = value

    if strict:
        result.unknown_keys = sorted(k for k in env if k not in schema_keys)

    return result
