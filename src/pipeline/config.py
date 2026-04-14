from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.pipeline.metrics import SUPPORTED_TRANSFORMS


@dataclass(frozen=True)
class SeriesDefinition:
    id: str
    label: str
    page: str
    category: str
    frequency: str
    format: str
    source: str
    transforms: list[str]
    default_transform: str
    notes: str = ""


def load_series_definitions(config_path: Path) -> tuple[dict[str, str], list[SeriesDefinition]]:
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)

    app_config = payload.get("app", {})
    raw_series = payload.get("series", [])
    definitions = [SeriesDefinition(**item) for item in raw_series]
    validate_definitions(definitions)
    return app_config, definitions


def validate_definitions(definitions: list[SeriesDefinition]) -> None:
    seen_ids: set[str] = set()
    valid_frequencies = {"daily", "weekly", "monthly", "quarterly"}

    for definition in definitions:
        if definition.id in seen_ids:
            raise ValueError(f"Duplicate series id found in config: {definition.id}")
        seen_ids.add(definition.id)

        if definition.frequency not in valid_frequencies:
            raise ValueError(
                f"{definition.id} has unsupported frequency '{definition.frequency}'."
            )

        if definition.default_transform not in definition.transforms:
            raise ValueError(
                f"{definition.id} default_transform must be included in transforms."
            )

        for transform in definition.transforms:
            if transform not in SUPPORTED_TRANSFORMS:
                raise ValueError(
                    f"{definition.id} uses unsupported transform '{transform}'."
                )
