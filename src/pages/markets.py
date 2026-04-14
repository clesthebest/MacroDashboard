from __future__ import annotations

import streamlit as st

from src.components.charts import plot_comparison_chart
from src.pages.base import render_page_header, render_series_grid
from src.pipeline.service import MacroDataService
from src.state import SidebarFilters


COMPARISON_SERIES = ["SP500", "NASDAQCOM", "DJIA"]


def render(service: MacroDataService, filters: SidebarFilters) -> None:
    render_page_header(
        "Markets",
        "Major U.S. equity benchmarks and volatility from FRED.",
    )

    comparison_frame = service.get_comparison_frame(
        series_ids=COMPARISON_SERIES,
        transform="indexed_100",
        start_date=filters.start_date,
        end_date=filters.end_date,
        use_default_window=filters.use_default_windows,
    )
    st.plotly_chart(
        plot_comparison_chart(comparison_frame, "Indexed Equity Comparison (Base = 100)"),
        use_container_width=True,
        key="markets_equity_comparison_chart",
    )

    definitions = service.get_definitions_for_page(filters.page, filters.categories)
    render_series_grid(service, definitions, filters, "markets")


def get_categories(service: MacroDataService) -> list[str]:
    return service.list_categories_for_page("markets")
