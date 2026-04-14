from __future__ import annotations

from src.pages.base import render_page_header, render_series_grid
from src.pipeline.service import MacroDataService
from src.state import SidebarFilters


def render(service: MacroDataService, filters: SidebarFilters) -> None:
    render_page_header(
        "Growth",
        "Output, consumer activity, production, and housing indicators.",
    )
    definitions = service.get_definitions_for_page(filters.page, filters.categories)
    render_series_grid(service, definitions, filters, "growth")


def get_categories(service: MacroDataService) -> list[str]:
    return service.list_categories_for_page("growth")
