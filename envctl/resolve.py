"""Resolve a target name through aliases, then validate it exists in the store."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envctl.alias import load_aliases
from envctl.env_store import EnvStore


@dataclass
class ResolveResult:
    raw_name: str
    resolved_name: str
    alias_used: bool
    exists: bool
    env: dict[str, str] = field(default_factory=dict)

    def summary(self) -> str:
        if not self.exists:
            return f"Target '{self.resolved_name}' not found."
        if self.alias_used:
            return (
                f"Alias '{self.raw_name}' resolved to '{self.resolved_name}' "
                f"({len(self.env)} key(s))."
            )
        return f"Target '{self.resolved_name}' loaded ({len(self.env)} key(s))."


def resolve_target(
    name: str,
    store: EnvStore,
    *,
    follow_alias: bool = True,
) -> ResolveResult:
    """Resolve *name* to a concrete target, optionally following aliases.

    Parameters
    ----------
    name:
        The raw target name or alias supplied by the caller.
    store:
        An :class:`EnvStore` instance used to load the environment.
    follow_alias:
        When *True* (default), look up ``name`` in the alias registry and
        substitute the canonical target name if a match is found.
    """
    resolved = name
    alias_used = False

    if follow_alias:
        aliases = load_aliases(store.base_dir)
        if name in aliases:
            resolved = aliases[name]
            alias_used = True

    targets = store.list_targets()
    if resolved not in targets:
        return ResolveResult(
            raw_name=name,
            resolved_name=resolved,
            alias_used=alias_used,
            exists=False,
        )

    env = store.load(resolved)
    return ResolveResult(
        raw_name=name,
        resolved_name=resolved,
        alias_used=alias_used,
        exists=True,
        env=env,
    )
