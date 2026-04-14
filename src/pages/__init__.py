from src.pages.growth import get_categories as growth_categories
from src.pages.growth import render as render_growth
from src.pages.inflation import get_categories as inflation_categories
from src.pages.inflation import render as render_inflation
from src.pages.labor import get_categories as labor_categories
from src.pages.labor import render as render_labor
from src.pages.markets import get_categories as markets_categories
from src.pages.markets import render as render_markets
from src.pages.overview import get_categories as overview_categories
from src.pages.overview import render as render_overview
from src.pages.rates import get_categories as rates_categories
from src.pages.rates import render as render_rates


PAGE_REGISTRY = {
    "overview": {
        "label": "Overview",
        "render": render_overview,
        "categories": overview_categories,
    },
    "rates": {
        "label": "Rates",
        "render": render_rates,
        "categories": rates_categories,
    },
    "inflation": {
        "label": "Inflation",
        "render": render_inflation,
        "categories": inflation_categories,
    },
    "labor": {
        "label": "Labor",
        "render": render_labor,
        "categories": labor_categories,
    },
    "growth": {
        "label": "Growth",
        "render": render_growth,
        "categories": growth_categories,
    },
    "markets": {
        "label": "Markets",
        "render": render_markets,
        "categories": markets_categories,
    },
}
