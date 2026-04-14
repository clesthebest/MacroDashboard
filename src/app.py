from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st

from src.pages import PAGE_REGISTRY
from src.pipeline.service import MacroDataService
from src.state import SidebarFilters


def main() -> None:
    load_dotenv()

    st.set_page_config(
        page_title="US Macro Dashboard",
        page_icon="US",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    service = MacroDataService(config_path=Path("config/series.yaml"))
    page_key = render_sidebar(service)

    filters = SidebarFilters(
        page=page_key,
        categories=st.session_state.get(f"selected_categories_{page_key}", []),
        use_default_windows=st.session_state["use_default_windows"],
        start_date=st.session_state.get("global_start_date"),
        end_date=st.session_state.get("global_end_date"),
    )

    PAGE_REGISTRY[page_key]["render"](service, filters)


def render_sidebar(service: MacroDataService) -> str:
    all_page_keys = list(PAGE_REGISTRY)

    with st.sidebar:
        st.title("US Macro Dashboard")
        page_key = st.radio(
            "Page",
            options=all_page_keys,
            format_func=lambda key: PAGE_REGISTRY[key]["label"],
        )

        st.divider()
        st.subheader("Filters")

        use_default_windows = st.checkbox(
            "Use frequency defaults",
            value=st.session_state.get("use_default_windows", True),
            key="use_default_windows",
            help=(
                "Daily/weekly series default to 1 year, monthly to 5 years, "
                "and quarterly to 10 years."
            ),
        )

        default_end = date.today()
        default_start = default_end - timedelta(days=365 * 5)

        if use_default_windows:
            st.caption(
                "Using per-series default history windows to avoid misleading "
                "mixed-frequency comparisons."
            )
            st.session_state["global_start_date"] = None
            st.session_state["global_end_date"] = None
        else:
            start_date, end_date = st.date_input(
                "Date range",
                value=(
                    st.session_state.get("global_start_date") or default_start,
                    st.session_state.get("global_end_date") or default_end,
                ),
                min_value=date(1950, 1, 1),
                max_value=default_end,
            )
            st.session_state["global_start_date"] = start_date
            st.session_state["global_end_date"] = end_date

        categories = service.list_categories_for_page(page_key)
        st.multiselect(
            "Category",
            options=categories,
            default=categories,
            key=f"selected_categories_{page_key}",
        )

        st.caption(
            "Data source: FRED. Lower-frequency data is shown on its native "
            "observation schedule unless otherwise labeled."
        )

    return page_key
