"""Export environment variable sets to various formats."""

from __future__ import annotations

import json
from typing import Dict, Literal

ExportFormat = Literal["dotenv", "json", "shell"]


def export_env(env: Dict[str, str], fmt: ExportFormat = "dotenv") -> str:
    """Serialize an env dict to the requested format string."""
    if fmt == "dotenv":
        return _to_dotenv(env)
    if fmt == "json":
        return _to_json(env)
    if fmt == "shell":
        return _to_shell(env)
    raise ValueError(f"Unsupported export format: {fmt!r}")


def _to_dotenv(env: Dict[str, str]) -> str:
    lines = []
    for key, value in sorted(env.items()):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def _to_json(env: Dict[str, str]) -> str:
    return json.dumps(dict(sorted(env.items())), indent=2) + "\n"


def _to_shell(env: Dict[str, str]) -> str:
    lines = ["#!/usr/bin/env sh"]
    for key, value in sorted(env.items()):
        escaped = value.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + "\n"


def import_dotenv(text: str) -> Dict[str, str]:
    """Parse a .env-formatted string and return a dict of key/value pairs."""
    env: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        value = raw_value.strip()
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        env[key] = value
    return env
