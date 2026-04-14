from __future__ import annotations

import streamlit as st

from src.pipeline.service import SeriesPayload
from src.utils.formatting import (
    format_change,
    format_date_label,
    format_value,
    humanize_transform,
)


def render_metric_summary(payload: SeriesPayload) -> None:
    latest_value = payload.summary["latest_value"]
    previous_value = payload.summary["previous_value"]
    latest_date = payload.summary["latest_date"]
    delta = payload.summary["delta"]

    metric_label = humanize_transform(payload.transform)
    value_text = format_value(
        latest_value,
        payload.definition.format,
        payload.transform,
    )
    delta_text = format_change(
        delta,
        payload.definition.format,
        payload.transform,
        previous_value,
    )

    st.metric(
        label=f"Latest {metric_label}",
        value=value_text,
        delta=delta_text,
    )

    if latest_date is not None:
        st.caption(f"Latest observation: {format_date_label(latest_date)}")


def render_series_attribution(payload: SeriesPayload) -> None:
    st.caption(
        f"Source: {payload.definition.source} | "
        f"Series ID: {payload.definition.id} | "
        f"Frequency: {payload.definition.frequency.title()}"
    )
