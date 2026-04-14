from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.pipeline.config import SeriesDefinition
from src.utils.formatting import humanize_transform


COLOR_SEQUENCE = ["#0f4c5c", "#e36414", "#6f1d1b", "#2c7da0", "#8d99ae"]


def plot_series_chart(
    frame: pd.DataFrame,
    definition: SeriesDefinition,
    transform: str,
) -> go.Figure:
    figure = px.line(
        frame,
        x="date",
        y="value",
        template="plotly_white",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    figure.update_layout(
        title=f"{definition.label} ({humanize_transform(transform)})",
        margin={"l": 8, "r": 8, "t": 48, "b": 8},
        height=340,
        xaxis_title="",
        yaxis_title="",
    )
    figure.update_traces(line={"width": 2.5})
    return figure


def plot_comparison_chart(
    frame: pd.DataFrame,
    title: str,
) -> go.Figure:
    figure = px.line(
        frame,
        x="date",
        y="value",
        color="label",
        template="plotly_white",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    figure.update_layout(
        title=title,
        margin={"l": 8, "r": 8, "t": 48, "b": 8},
        height=380,
        xaxis_title="",
        yaxis_title="",
        legend_title="",
    )
    figure.update_traces(line={"width": 2.5})
    return figure


def plot_dual_axis_comparison_chart(
    frame: pd.DataFrame,
    title: str,
    secondary_series_ids: set[str],
    primary_axis_title: str = "",
    secondary_axis_title: str = "",
) -> go.Figure:
    figure = make_subplots(specs=[[{"secondary_y": True}]])

    labels = list(dict.fromkeys(frame["label"].tolist()))
    color_map = {
        label: COLOR_SEQUENCE[index % len(COLOR_SEQUENCE)]
        for index, label in enumerate(labels)
    }

    for label in labels:
        series_frame = frame[frame["label"] == label]
        series_id = series_frame["series_id"].iloc[0]
        is_secondary = series_id in secondary_series_ids
        figure.add_trace(
            go.Scatter(
                x=series_frame["date"],
                y=series_frame["value"],
                mode="lines",
                name=label,
                line={"width": 2.5, "color": color_map[label]},
            ),
            secondary_y=is_secondary,
        )

    figure.update_layout(
        title=title,
        template="plotly_white",
        margin={"l": 8, "r": 8, "t": 48, "b": 8},
        height=380,
        xaxis_title="",
        legend_title="",
    )
    figure.update_yaxes(title_text=primary_axis_title, secondary_y=False)
    figure.update_yaxes(title_text=secondary_axis_title, secondary_y=True)
    return figure


def plot_yield_curve_chart(
    frame: pd.DataFrame,
    title: str,
) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=frame["maturity_label"],
            y=frame["value"],
            mode="lines+markers",
            line={"width": 3, "color": COLOR_SEQUENCE[0]},
            marker={"size": 8, "color": COLOR_SEQUENCE[1]},
            hovertemplate=(
                "%{x}: %{y:.2f}%<br>"
                "Series: %{customdata[0]}<br>"
                "Obs date: %{customdata[1]|%b %d, %Y}<extra></extra>"
            ),
            customdata=frame[["series_id", "observation_date"]],
            name="Yield Curve",
        )
    )
    figure.update_layout(
        title=title,
        template="plotly_white",
        margin={"l": 8, "r": 8, "t": 48, "b": 8},
        height=360,
        xaxis_title="Maturity",
        yaxis_title="Yield (%)",
        showlegend=False,
    )
    return figure
