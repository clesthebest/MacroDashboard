from __future__ import annotations

import streamlit as st

from src.components.charts import plot_comparison_chart
from src.components.risk_panel import render_risk_panel
from src.pages.base import render_page_header, render_series_grid
from src.pipeline.service import MacroDataService
from src.state import SidebarFilters


FEATURED_SERIES = ["DFF", "CPIAUCSL", "UNRATE", "GDPC1"]
COMPARISON_SERIES = ["SP500", "NASDAQCOM", "DJIA"]


def render(service: MacroDataService, filters: SidebarFilters) -> None:
    render_page_header(
        "Overview",
        "A quick macro pulse across policy, inflation, labor, growth, and markets.",
    )

    st.markdown("### Featured Metrics")
    featured = [service.get_definition(series_id) for series_id in FEATURED_SERIES]
    render_series_grid(service, featured, filters, "overview_featured")

    st.markdown("### Market Comparison")
    comparison_frame = service.get_comparison_frame(
        series_ids=COMPARISON_SERIES,
        transform="indexed_100",
        start_date=filters.start_date,
        end_date=filters.end_date,
        use_default_window=filters.use_default_windows,
    )
    st.plotly_chart(
        plot_comparison_chart(comparison_frame, "Indexed Equity Performance (Base = 100)"),
        use_container_width=True,
        key="overview_market_comparison_chart",
    )

    render_risk_panel(
        service=service,
        start_date=filters.start_date,
        end_date=filters.end_date,
        use_default_window=filters.use_default_windows,
    )

    st.markdown("### Full Dataset")
    definitions = service.get_definitions_for_page(filters.page, filters.categories)
    render_series_grid(service, definitions, filters, "overview_all")


def get_categories(service: MacroDataService) -> list[str]:
    return service.list_categories_for_page("overview")
