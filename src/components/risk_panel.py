from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.components.charts import (
    plot_comparison_chart,
    plot_dual_axis_comparison_chart,
    plot_series_chart,
    plot_yield_curve_chart,
)
from src.components.metric_card import render_metric_summary, render_series_attribution
from src.pipeline.service import MacroDataService


RISK_DAILY_SERIES = ["T10Y2Y", "T10Y3M", "BAMLH0A0HYM2", "VIXCLS"]
RISK_MONTHLY_SERIES = ["UNRATE"]
YIELD_CURVE_SERIES = [
    ("DGS1MO", "1M", 1 / 12),
    ("DGS3MO", "3M", 3 / 12),
    ("DGS6MO", "6M", 6 / 12),
    ("DGS1", "1Y", 1),
    ("DGS2", "2Y", 2),
    ("DGS3", "3Y", 3),
    ("DGS5", "5Y", 5),
    ("DGS7", "7Y", 7),
    ("DGS10", "10Y", 10),
    ("DGS20", "20Y", 20),
    ("DGS30", "30Y", 30),
]


def render_risk_panel(
    service: MacroDataService,
    start_date,
    end_date,
    use_default_window: bool,
) -> None:
    st.subheader("Risk Panel")
    st.caption(
        "Daily market stress indicators are shown together below. "
        "Monthly unemployment stays on its own chart to preserve the native frequency."
    )
    show_vix = st.toggle(
        "Show VIX on daily risk chart",
        value=False,
        help="Turn VIX on when you want the volatility overlay, or keep it off for a cleaner spread view.",
        key="risk_panel_show_vix",
    )

    all_ids = RISK_DAILY_SERIES + RISK_MONTHLY_SERIES
    columns = st.columns(len(all_ids))
    for index, series_id in enumerate(all_ids):
        definition = service.get_definition(series_id)
        payload = service.get_series_payload(
            definition=definition,
            start_date=start_date,
            end_date=end_date,
            use_default_window=use_default_window,
        )
        with columns[index]:
            st.markdown(f"**{definition.label}**")
            render_metric_summary(payload)
            render_series_attribution(payload)

    daily_series_ids = RISK_DAILY_SERIES if show_vix else [
        series_id for series_id in RISK_DAILY_SERIES if series_id != "VIXCLS"
    ]
    daily_frame = service.get_comparison_frame(
        series_ids=daily_series_ids,
        transform="level",
        start_date=start_date,
        end_date=end_date,
        use_default_window=use_default_window,
    )
    if show_vix:
        figure = plot_dual_axis_comparison_chart(
            daily_frame,
            "Daily Risk Indicators",
            secondary_series_ids={"VIXCLS"},
            primary_axis_title="Spread / OAS (%)",
            secondary_axis_title="VIX",
        )
    else:
        figure = plot_comparison_chart(
            daily_frame,
            "Daily Risk Indicators",
        )
        figure.update_yaxes(title_text="Spread / OAS (%)")

    st.plotly_chart(
        figure,
        use_container_width=True,
        key=f"risk_panel_daily_indicators_chart_{show_vix}",
    )

    unemployment = service.get_series_payload(
        definition=service.get_definition("UNRATE"),
        transform="level",
        start_date=start_date,
        end_date=end_date,
        use_default_window=use_default_window,
    )
    st.plotly_chart(
        plot_series_chart(unemployment.frame, unemployment.definition, unemployment.transform),
        use_container_width=True,
        key="risk_panel_unrate_chart",
    )

    st.markdown("### Treasury Yield Curve")
    show_yield_curve = st.toggle(
        "Show Treasury yield curve snapshot",
        value=True,
        help="Plot the Treasury curve using the latest available observation on or before the selected date.",
        key="risk_panel_show_yield_curve",
    )
    if not show_yield_curve:
        return

    selected_curve_date = st.date_input(
        "Yield curve date",
        value=end_date or date.today(),
        max_value=date.today(),
        key="risk_panel_yield_curve_date",
    )
    curve_frame = build_yield_curve_frame(service, selected_curve_date)
    if curve_frame.empty:
        st.warning("No Treasury curve observations were available on or before the selected date.")
        return

    latest_curve_date = curve_frame["observation_date"].max()
    earliest_curve_date = curve_frame["observation_date"].min()
    if earliest_curve_date == latest_curve_date:
        st.caption(
            f"Using Treasury observations from {latest_curve_date.strftime('%b %d, %Y')}."
        )
    else:
        st.caption(
            "Using the most recent available observations on or before the selected date. "
            f"Points range from {earliest_curve_date.strftime('%b %d, %Y')} "
            f"to {latest_curve_date.strftime('%b %d, %Y')}."
        )

    st.plotly_chart(
        plot_yield_curve_chart(
            curve_frame,
            f"Treasury Yield Curve Snapshot ({selected_curve_date.strftime('%b %d, %Y')})",
        ),
        use_container_width=True,
        key=f"risk_panel_yield_curve_{selected_curve_date.isoformat()}",
    )


def build_yield_curve_frame(
    service: MacroDataService,
    selected_date: date,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for series_id, maturity_label, maturity_years in YIELD_CURVE_SERIES:
        observation = service.get_latest_observation_on_or_before(series_id, selected_date)
        if observation is None:
            continue
        records.append(
            {
                "series_id": series_id,
                "maturity_label": maturity_label,
                "maturity_years": maturity_years,
                "value": float(observation["value"]),
                "observation_date": pd.Timestamp(observation["date"]),
            }
        )

    if not records:
        return pd.DataFrame(
            columns=[
                "series_id",
                "maturity_label",
                "maturity_years",
                "value",
                "observation_date",
            ]
        )

    return pd.DataFrame(records).sort_values("maturity_years").reset_index(drop=True)
