# US Macro Dashboard

A modular Streamlit dashboard for tracking U.S. macro indicators with FRED as the primary data source.

## What it includes

- Sidebar-driven navigation for Overview, Rates, Inflation, Labor, Growth, and Markets
- Config-driven series definitions from `config/series.yaml`
- Reusable FRED client and generic fetch/normalize/transform pipeline
- Local raw and processed caching under `data/cache`
- Plotly charts with latest value, prior-period comparison, source attribution, and series IDs
- Indexed equity comparison for `SP500`, `NASDAQCOM`, and `DJIA`
- Risk panel covering `T10Y2Y`, `T10Y3M`, `BAMLH0A0HYM2`, `VIXCLS`, and `UNRATE`

## Project structure

```text
.
|-- app.py
|-- config/
|   `-- series.yaml
|-- data/
|   `-- cache/
|       |-- processed/
|       `-- raw/
|-- README.md
|-- requirements.txt
`-- src/
    |-- app.py
    |-- clients/
    |   |-- cache.py
    |   `-- fred_client.py
    |-- components/
    |   |-- charts.py
    |   |-- metric_card.py
    |   `-- risk_panel.py
    |-- pages/
    |   |-- base.py
    |   |-- growth.py
    |   |-- inflation.py
    |   |-- labor.py
    |   |-- markets.py
    |   |-- overview.py
    |   `-- rates.py
    |-- pipeline/
    |   |-- config.py
    |   |-- metrics.py
    |   `-- service.py
    `-- utils/
        `-- formatting.py
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and optionally add a `FRED_API_KEY`.

The app works without a key by falling back to the public FRED CSV endpoint. If you add an API key, the dashboard will use the official FRED observations API.

## Run

```bash
streamlit run app.py
```

## Notes

- Daily and weekly series default to a 1-year history window.
- Monthly series default to 5 years.
- Quarterly series default to 10 years.
- Lower-frequency data is kept on its native observation schedule and is not forward-filled into daily charts.
