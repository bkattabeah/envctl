"""Search for keys or values across environment targets."""

from dataclasses import dataclass, field
from typing import Optional
from envctl.env_store import EnvStore


@dataclass
class SearchMatch:
    target: str
    key: str
    value: str
    matched_on: str  # 'key' | 'value' | 'both'


@dataclass
class SearchResult:
    query: str
    matches: list = field(default_factory=list)

    @property
    def has_matches(self) -> bool:
        return len(self.matches) > 0

    def summary(self) -> str:
        if not self.has_matches:
            return f"No matches found for '{self.query}'."
        return f"Found {len(self.matches)} match(es) for '{self.query}'."

    def targets_matched(self) -> list:
        seen = []
        for m in self.matches:
            if m.target not in seen:
                seen.append(m.target)
        return seen


def search_envs(
    store: EnvStore,
    query: str,
    targets: Optional[list] = None,
    keys_only: bool = False,
    values_only: bool = False,
    case_sensitive: bool = False,
) -> SearchResult:
    """Search for a query string across keys and/or values in env targets."""
    result = SearchResult(query=query)
    all_targets = targets if targets is not None else store.list_targets()
    needle = query if case_sensitive else query.lower()

    for target in all_targets:
        env = store.load(target)
        for key, value in env.items():
            k = key if case_sensitive else key.lower()
            v = value if case_sensitive else value.lower()

            in_key = not values_only and needle in k
            in_val = not keys_only and needle in v

            if in_key and in_val:
                matched_on = "both"
            elif in_key:
                matched_on = "key"
            elif in_val:
                matched_on = "value"
            else:
                continue

            result.matches.append(
                SearchMatch(target=target, key=key, value=value, matched_on=matched_on)
            )

    return result
