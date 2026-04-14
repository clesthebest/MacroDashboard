from __future__ import annotations

from typing import Iterable

import streamlit as st

from src.components.charts import plot_series_chart
from src.components.metric_card import render_metric_summary, render_series_attribution
from src.pipeline.config import SeriesDefinition
from src.pipeline.service import MacroDataService
from src.state import SidebarFilters
from src.utils.formatting import humanize_transform


def render_page_header(title: str, description: str) -> None:
    st.title(title)
    st.caption(description)


def render_series_grid(
    service: MacroDataService,
    definitions: Iterable[SeriesDefinition],
    filters: SidebarFilters,
    state_prefix: str,
) -> None:
    definitions = list(definitions)
    if not definitions:
        st.info("No series match the current filter selection.")
        return

    columns = st.columns(2)
    for index, definition in enumerate(definitions):
        with columns[index % 2]:
            render_series_card(service, definition, filters, state_prefix)


def render_series_card(
    service: MacroDataService,
    definition: SeriesDefinition,
    filters: SidebarFilters,
    state_prefix: str,
) -> None:
    transform_key = f"{state_prefix}_{definition.id}_transform"
    default_index = definition.transforms.index(definition.default_transform)

    with st.container(border=True):
        header_left, header_right = st.columns([3, 2])
        with header_left:
            st.subheader(definition.label)
            if definition.notes:
                st.caption(definition.notes)

        with header_right:
            transform = st.selectbox(
                "Transform",
                options=definition.transforms,
                index=default_index,
                key=transform_key,
                format_func=humanize_transform,
                label_visibility="collapsed",
            )

        try:
            payload = service.get_series_payload(
                definition=definition,
                transform=transform,
                start_date=filters.start_date,
                end_date=filters.end_date,
                use_default_window=filters.use_default_windows,
            )
        except Exception as error:
            st.error(f"Unable to load {definition.id}: {error}")
            return

        render_metric_summary(payload)
        if payload.frame.empty:
            st.warning("No observations were returned for the selected window.")
            return

        st.plotly_chart(
            plot_series_chart(payload.frame, definition, transform),
            use_container_width=True,
            key=f"{state_prefix}_{definition.id}_{transform}_chart",
        )
        render_series_attribution(payload)
