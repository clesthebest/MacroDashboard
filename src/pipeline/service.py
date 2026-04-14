from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import os
from pathlib import Path

import pandas as pd

from src.clients import CacheManager, FredClient
from src.pipeline.config import SeriesDefinition, load_series_definitions
from src.pipeline.metrics import apply_transform, normalize_series, summarize_series


DEFAULT_WINDOWS = {
    "daily": timedelta(days=365),
    "weekly": timedelta(days=365),
    "monthly": timedelta(days=365 * 5),
    "quarterly": timedelta(days=365 * 10),
}


@dataclass(frozen=True)
class SeriesPayload:
    definition: SeriesDefinition
    transform: str
    frame: pd.DataFrame
    summary: dict[str, object]
    start_date: date | None
    end_date: date | None


class MacroDataService:
    def __init__(self, config_path: Path) -> None:
        self.app_config, self.definitions = load_series_definitions(config_path)
        self.definition_map = {definition.id: definition for definition in self.definitions}
        self.client = FredClient(api_key=os.getenv("FRED_API_KEY") or None)
        self.cache = CacheManager(root=Path("data/cache"))
        self.cache_ttl_hours = int(os.getenv("FRED_CACHE_TTL_HOURS", "24"))

    def list_categories_for_page(self, page_key: str) -> list[str]:
        if page_key == "overview":
            return sorted({definition.page for definition in self.definitions})

        page_name = page_key.title()
        return sorted(
            {definition.category for definition in self.definitions if definition.page == page_name}
        )

    def get_definitions_for_page(
        self,
        page_key: str,
        categories: list[str] | None = None,
    ) -> list[SeriesDefinition]:
        if page_key == "overview":
            candidates = self.definitions
            if categories:
                candidates = [definition for definition in candidates if definition.page in categories]
            return candidates

        page_name = page_key.title()
        candidates = [definition for definition in self.definitions if definition.page == page_name]
        if categories:
            candidates = [definition for definition in candidates if definition.category in categories]
        return candidates

    def get_definition(self, series_id: str) -> SeriesDefinition:
        return self.definition_map[series_id]

    def get_series_payload(
        self,
        definition: SeriesDefinition,
        transform: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        use_default_window: bool = True,
    ) -> SeriesPayload:
        selected_transform = transform or definition.default_transform
        raw = self._get_raw_series(definition.id)
        normalized = normalize_series(raw)
        resolved_start, resolved_end = self._resolve_window(
            definition.frequency,
            start_date,
            end_date,
            use_default_window,
        )

        raw_mtime = self.cache.raw_path(definition.id).stat().st_mtime_ns
        cache_key = self.cache.build_processed_key(
            {
                "series_id": definition.id,
                "transform": selected_transform,
                "start_date": resolved_start,
                "end_date": resolved_end,
                "raw_mtime": raw_mtime,
            }
        )

        processed = self.cache.load_processed(definition.id, cache_key)
        if processed is None:
            filtered = self._filter_window(normalized, resolved_start, resolved_end)
            processed = apply_transform(filtered, selected_transform, definition.frequency)
            self.cache.save_processed(definition.id, cache_key, processed)

        summary = summarize_series(processed)
        return SeriesPayload(
            definition=definition,
            transform=selected_transform,
            frame=processed,
            summary=summary,
            start_date=resolved_start,
            end_date=resolved_end,
        )

    def get_comparison_frame(
        self,
        series_ids: list[str],
        transform: str,
        start_date: date | None = None,
        end_date: date | None = None,
        use_default_window: bool = True,
    ) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        for series_id in series_ids:
            definition = self.get_definition(series_id)
            payload = self.get_series_payload(
                definition=definition,
                transform=transform,
                start_date=start_date,
                end_date=end_date,
                use_default_window=use_default_window,
            )
            frame = payload.frame.copy()
            frame["label"] = definition.label
            frames.append(frame)

        if not frames:
            return pd.DataFrame(columns=["date", "value", "label"])
        return pd.concat(frames, ignore_index=True)

    def get_latest_observation_on_or_before(
        self,
        series_id: str,
        target_date: date,
    ) -> pd.Series | None:
        raw = self._get_raw_series(series_id)
        normalized = normalize_series(raw)
        eligible = normalized[normalized["date"] <= pd.Timestamp(target_date)]
        if eligible.empty:
            return None
        return eligible.iloc[-1]

    def _get_raw_series(self, series_id: str) -> pd.DataFrame:
        cached = self.cache.load_raw(series_id)
        raw_path = self.cache.raw_path(series_id)
        cache_is_fresh = cached is not None and raw_path.exists() and self._is_fresh(raw_path)

        if cache_is_fresh:
            return cached

        try:
            fetched = self.client.fetch_series(series_id)
            self.cache.save_raw(series_id, fetched)
            return fetched
        except Exception:
            if cached is not None:
                return cached
            raise

    def _is_fresh(self, path: Path) -> bool:
        age_seconds = pd.Timestamp.utcnow().timestamp() - path.stat().st_mtime
        return age_seconds < self.cache_ttl_hours * 3600

    def _resolve_window(
        self,
        frequency: str,
        start_date: date | None,
        end_date: date | None,
        use_default_window: bool,
    ) -> tuple[date | None, date | None]:
        resolved_end = end_date or date.today()
        if use_default_window or start_date is None:
            resolved_start = resolved_end - DEFAULT_WINDOWS[frequency]
        else:
            resolved_start = start_date
        return resolved_start, resolved_end

    def _filter_window(
        self,
        frame: pd.DataFrame,
        start_date: date | None,
        end_date: date | None,
    ) -> pd.DataFrame:
        filtered = frame.copy()
        if start_date is not None:
            filtered = filtered[filtered["date"] >= pd.Timestamp(start_date)]
        if end_date is not None:
            filtered = filtered[filtered["date"] <= pd.Timestamp(end_date)]
        return filtered.reset_index(drop=True)
