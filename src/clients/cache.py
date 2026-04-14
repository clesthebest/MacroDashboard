from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


class CacheManager:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.raw_dir = root / "raw"
        self.processed_dir = root / "processed"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def raw_path(self, series_id: str) -> Path:
        return self.raw_dir / f"{series_id}.csv"

    def load_raw(self, series_id: str) -> pd.DataFrame | None:
        path = self.raw_path(series_id)
        if not path.exists():
            return None
        return pd.read_csv(path, parse_dates=["date"])

    def save_raw(self, series_id: str, frame: pd.DataFrame) -> Path:
        path = self.raw_path(series_id)
        frame.to_csv(path, index=False)
        return path

    def processed_path(self, series_id: str, cache_key: str) -> Path:
        return self.processed_dir / f"{series_id}_{cache_key}.csv"

    def build_processed_key(self, payload: dict[str, Any]) -> str:
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

    def load_processed(self, series_id: str, cache_key: str) -> pd.DataFrame | None:
        path = self.processed_path(series_id, cache_key)
        if not path.exists():
            return None
        return pd.read_csv(path, parse_dates=["date"])

    def save_processed(
        self,
        series_id: str,
        cache_key: str,
        frame: pd.DataFrame,
    ) -> Path:
        path = self.processed_path(series_id, cache_key)
        frame.to_csv(path, index=False)
        return path
