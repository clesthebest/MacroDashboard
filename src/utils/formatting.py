from __future__ import annotations

from datetime import date, datetime
import math

import pandas as pd


TRANSFORM_LABELS = {
    "level": "Level",
    "change": "Period Change",
    "pct_change": "Percent Change",
    "yoy": "Year over Year",
    "indexed_100": "Indexed to 100",
}


def humanize_transform(transform: str) -> str:
    return TRANSFORM_LABELS.get(transform, transform.replace("_", " ").title())


def format_value(
    value: float | int | None,
    base_format: str,
    transform: str,
) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"

    if transform in {"pct_change", "yoy"}:
        return f"{value:,.2f}%"

    if transform == "indexed_100":
        return f"{value:,.1f}"

    if base_format == "percent":
        return f"{value:,.2f}%"
    if base_format == "currency_billions":
        return f"${value / 1_000:,.2f}B"
    if base_format == "integer":
        return f"{value:,.0f}"
    if base_format == "index":
        return f"{value:,.2f}"
    return f"{value:,.2f}"


def format_change(
    delta: float | int | None,
    base_format: str,
    transform: str,
    previous_value: float | int | None,
) -> str:
    if delta is None or previous_value is None:
        return "No prior point"

    if transform in {"pct_change", "yoy"}:
        return f"{delta:+,.2f} pp"
    if transform == "indexed_100":
        return f"{delta:+,.2f}"
    if base_format == "percent":
        return f"{delta:+,.2f} pp"
    if base_format == "currency_billions":
        return f"{delta / 1_000:+,.2f}B"
    if base_format == "integer":
        return f"{delta:+,.0f}"
    return f"{delta:+,.2f}"


def format_date_label(value: pd.Timestamp | datetime | date) -> str:
    return pd.Timestamp(value).strftime("%b %d, %Y")
