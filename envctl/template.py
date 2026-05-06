"""Template rendering for environment variable sets.

Allows users to render a target's env vars into a string template
using {{VAR_NAME}} placeholders.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envctl.env_store import EnvStore

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass
class TemplateResult:
    rendered: str
    missing_vars: List[str] = field(default_factory=list)
    used_vars: List[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """True when every placeholder was resolved."""
        return len(self.missing_vars) == 0

    def summary(self) -> str:
        lines = []
        if self.used_vars:
            lines.append(f"Resolved : {', '.join(sorted(self.used_vars))}")
        if self.missing_vars:
            lines.append(f"Missing  : {', '.join(sorted(self.missing_vars))}")
        if not lines:
            lines.append("No placeholders found in template.")
        return "\n".join(lines)


def render_template(template: str, env: Dict[str, str]) -> TemplateResult:
    """Substitute {{VAR}} placeholders in *template* using *env*."""
    missing: List[str] = []
    used: List[str] = []

    def replacer(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        if key in env:
            used.append(key)
            return env[key]
        missing.append(key)
        return match.group(0)  # leave unresolved placeholder as-is

    rendered = _PLACEHOLDER_RE.sub(replacer, template)
    return TemplateResult(
        rendered=rendered,
        missing_vars=list(dict.fromkeys(missing)),
        used_vars=list(dict.fromkeys(used)),
    )


def render_template_for_target(
    store: EnvStore, target: str, template: str
) -> TemplateResult:
    """Load *target* from *store* and render *template* against it."""
    env = store.load(target)
    return render_template(template, env)
