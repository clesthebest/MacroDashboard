from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SidebarFilters:
    page: str
    categories: list[str]
    use_default_windows: bool
    start_date: date | None
    end_date: date | None
