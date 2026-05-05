"""Core module for loading, storing, and managing environment variable sets."""

import os
import json
from pathlib import Path
from typing import Dict, Optional


ENV_FILE_EXTENSION = ".env.json"


class EnvStore:
    """Manages named environment variable sets stored as JSON files."""

    def __init__(self, store_dir: str = ".envctl"):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def _target_path(self, target: str) -> Path:
        return self.store_dir / f"{target}{ENV_FILE_EXTENSION}"

    def save(self, target: str, env_vars: Dict[str, str]) -> None:
        """Persist an environment variable set for a named target."""
        if not target.isidentifier():
            raise ValueError(f"Invalid target name: '{target}'. Must be a valid identifier.")
        path = self._target_path(target)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(env_vars, f, indent=2, sort_keys=True)

    def load(self, target: str) -> Dict[str, str]:
        """Load environment variables for a named target."""
        path = self._target_path(target)
        if not path.exists():
            raise FileNotFoundError(f"No environment set found for target: '{target}'")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Invalid format in {path}: expected a JSON object.")
        return {str(k): str(v) for k, v in data.items()}

    def list_targets(self) -> list:
        """Return all available target names."""
        return sorted(
            p.stem
            for p in self.store_dir.glob(f"*{ENV_FILE_EXTENSION}")
        )

    def delete(self, target: str) -> None:
        """Remove a stored environment set."""
        path = self._target_path(target)
        if not path.exists():
            raise FileNotFoundError(f"No environment set found for target: '{target}'")
        path.unlink()

    def load_from_dotenv(self, filepath: str) -> Dict[str, str]:
        """Parse a .env file into a dictionary (KEY=VALUE format)."""
        env_vars: Dict[str, str] = {}
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
        return env_vars
