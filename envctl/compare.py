"""Compare multiple targets side-by-side and produce a structured result."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from envctl.env_store import EnvStore


@dataclass
class CompareResult:
    targets: List[str]
    all_keys: List[str]
    # matrix[key][target] = value or None if absent
    matrix: Dict[str, Dict[str, Optional[str]]]
    common_keys: List[str] = field(default_factory=list)
    unique_keys: Dict[str, List[str]] = field(default_factory=dict)

    def keys_for(self, target: str) -> Set[str]:
        return {k for k, tv in self.matrix.items() if tv.get(target) is not None}

    def has_divergence(self) -> bool:
        """True if any key has differing values across targets that all define it."""
        for key, tv in self.matrix.items():
            present = [v for v in tv.values() if v is not None]
            if len(present) > 1 and len(set(present)) > 1:
                return True
        return False

    def divergent_keys(self) -> List[str]:
        result = []
        for key, tv in self.matrix.items():
            present = [v for v in tv.values() if v is not None]
            if len(present) > 1 and len(set(present)) > 1:
                result.append(key)
        return sorted(result)


def compare_targets(store: EnvStore, targets: List[str]) -> CompareResult:
    """Load each target and build a comparison matrix."""
    if len(targets) < 2:
        raise ValueError("At least two targets are required for comparison.")

    envs: Dict[str, Dict[str, str]] = {}
    for t in targets:
        envs[t] = store.load(t)

    all_keys: List[str] = sorted({k for env in envs.values() for k in env})

    matrix: Dict[str, Dict[str, Optional[str]]] = {}
    for key in all_keys:
        matrix[key] = {t: envs[t].get(key) for t in targets}

    common_keys = [
        k for k in all_keys if all(matrix[k][t] is not None for t in targets)
    ]

    unique_keys: Dict[str, List[str]] = {t: [] for t in targets}
    for key in all_keys:
        present_in = [t for t in targets if matrix[key][t] is not None]
        if len(present_in) == 1:
            unique_keys[present_in[0]].append(key)

    return CompareResult(
        targets=targets,
        all_keys=all_keys,
        matrix=matrix,
        common_keys=common_keys,
        unique_keys=unique_keys,
    )
