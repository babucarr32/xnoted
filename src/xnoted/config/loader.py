from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, Dict
from xnoted.utils.dataDir import CUSTOM_XNOTED_PATH


class ConfigLoader:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.custom_path = Path(CUSTOM_XNOTED_PATH)

    def exists(self, path: Path) -> bool:
        return path.exists()

    def load(self) -> Dict[str, Any]:
        """
        Load and parse TOML config file.

        Returns:
            Dict[str, Any]: Parsed configuration dictionary.
        """
        if not self.exists(self.path):
            raise FileNotFoundError(f"Config file not found: {self.path}")

        with self.path.open("rb") as f:
            return tomllib.load(f)

    def load_custom(self) -> Dict[str, Any] | None:
        """
        Load and parse custom TOML config file.

        Returns:
            Dict[str, Any]: Parsed configuration dictionary.
        """
        if not self.exists(self.custom_path):
            return None

        with self.custom_path.open("rb") as f:
            return tomllib.load(f)

    def try_load(self) -> Dict[str, Any]:
        """
        Safe loader that returns empty dict instead of throwing.
        Useful for first-run / missing config scenarios.
        """
        try:
            return self.load()
        except FileNotFoundError:
            return {}

    def load_raw(self) -> bytes:
        """
        Returns raw TOML file content (rarely needed).
        """
        if not self.exists(self.path):
            raise FileNotFoundError(f"Config file not found: {self.path}")

        return self.path.read_bytes()
