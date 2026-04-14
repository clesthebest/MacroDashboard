from __future__ import annotations

from datetime import date
from io import StringIO

import pandas as pd
import requests


class FredClient:
    API_URL = "https://api.stlouisfed.org/fred/series/observations"
    GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"

    def __init__(self, api_key: str | None = None, timeout: int = 30) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def fetch_series(
        self,
        series_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> pd.DataFrame:
        if self.api_key:
            frame = self._fetch_json_api(series_id, start_date, end_date)
        else:
            frame = self._fetch_csv_fallback(series_id, start_date, end_date)

        if frame.empty:
            return pd.DataFrame(columns=["date", "value", "series_id"])

        frame["date"] = pd.to_datetime(frame["date"])
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        frame = frame.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)
        frame["series_id"] = series_id
        return frame[["date", "value", "series_id"]]

    def _fetch_json_api(
        self,
        series_id: str,
        start_date: date | None,
        end_date: date | None,
    ) -> pd.DataFrame:
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }
        if start_date:
            params["observation_start"] = start_date.isoformat()
        if end_date:
            params["observation_end"] = end_date.isoformat()

        response = requests.get(self.API_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        observations = payload.get("observations", [])
        frame = pd.DataFrame(observations)
        if frame.empty:
            return pd.DataFrame(columns=["date", "value"])
        return frame[["date", "value"]]

    def _fetch_csv_fallback(
        self,
        series_id: str,
        start_date: date | None,
        end_date: date | None,
    ) -> pd.DataFrame:
        params = {"id": series_id}
        if start_date:
            params["cosd"] = start_date.isoformat()
        if end_date:
            params["coed"] = end_date.isoformat()

        response = requests.get(self.GRAPH_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        frame = pd.read_csv(StringIO(response.text))
        if frame.empty:
            return pd.DataFrame(columns=["date", "value"])

        date_column = next(
            column
            for column in frame.columns
            if column.lower() in {"date", "observation_date"}
        )
        value_column = next(column for column in frame.columns if column != date_column)
        renamed = frame.rename(columns={date_column: "date", value_column: "value"})
        return renamed[["date", "value"]]
