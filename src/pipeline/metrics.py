from __future__ import annotations

import pandas as pd


SUPPORTED_TRANSFORMS = {
    "level",
    "change",
    "pct_change",
    "yoy",
    "indexed_100",
}


PERIODS_PER_YEAR = {
    "daily": 252,
    "weekly": 52,
    "monthly": 12,
    "quarterly": 4,
}


def normalize_series(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized["date"] = pd.to_datetime(normalized["date"])
    normalized["value"] = pd.to_numeric(normalized["value"], errors="coerce")
    normalized = normalized.dropna(subset=["value"]).sort_values("date")
    return normalized[["date", "value", "series_id"]].reset_index(drop=True)


def apply_transform(
    frame: pd.DataFrame,
    transform: str,
    frequency: str,
) -> pd.DataFrame:
    transformed = frame.copy()
    if transformed.empty:
        return transformed

    if transform == "level":
        pass
    elif transform == "change":
        transformed["value"] = transformed["value"].diff()
    elif transform == "pct_change":
        transformed["value"] = transformed["value"].pct_change() * 100
    elif transform == "yoy":
        periods = PERIODS_PER_YEAR[frequency]
        transformed["value"] = transformed["value"].pct_change(periods=periods) * 100
    elif transform == "indexed_100":
        valid_values = transformed["value"].dropna()
        if valid_values.empty:
            return transformed.iloc[0:0]
        first_valid = valid_values.iloc[0]
        transformed["value"] = transformed["value"] / first_valid * 100
    else:
        raise ValueError(f"Unsupported transform: {transform}")

    return transformed.dropna(subset=["value"]).reset_index(drop=True)


def summarize_series(frame: pd.DataFrame) -> dict[str, float | pd.Timestamp | None]:
    if frame.empty:
        return {
            "latest_date": None,
            "latest_value": None,
            "previous_value": None,
            "delta": None,
        }

    latest_row = frame.iloc[-1]
    previous_value = frame.iloc[-2]["value"] if len(frame) > 1 else None
    latest_value = latest_row["value"]
    delta = latest_value - previous_value if previous_value is not None else None

    return {
        "latest_date": latest_row["date"],
        "latest_value": latest_value,
        "previous_value": previous_value,
        "delta": delta,
    }
