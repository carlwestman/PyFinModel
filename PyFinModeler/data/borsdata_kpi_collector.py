# PyFinModeler/data/borsdata_kpi_collector.py

import requests
import base64
from typing import Dict

class BorsdataKPICollector:
    BASE_URL = "https://apiservice.borsdata.se/v1"

    def __init__(self, api_key: str):
        """
        Initialize the KPI Collector for Swedish/Nordic companies.

        Args:
            api_key: Your Börsdata API Key
        """
        self.api_key = api_key
        self.session = requests.Session()

        # Börsdata authentication: Basic Auth (username = api_key, password = empty)
        auth_string = f"{self.api_key}:"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        self.session.headers.update({
            "Authorization": f"Basic {auth_base64}"
        })

    def fetch_kpis(
        self,
        instrument_id: int,
        kpi_id: int,
        report_type: str = "year",  # 'year', 'r12', 'quarter'
        price_type: str = "mean"    # 'mean', 'low', 'high'
    ) -> Dict[str, float]:
        """
        Fetch historical KPI values for a specific instrument.

        Args:
            instrument_id: Company Instrument ID
            kpi_id: KPI ID
            report_type: 'year', 'r12', 'quarter'
            price_type: 'mean', 'low', 'high'

        Returns:
            Dictionary mapping {period: KPI value}, where period is "2024", "2024Q2", etc.
        """

        url = f"{self.BASE_URL}/instruments/{instrument_id}/kpis/{kpi_id}/{report_type}/{price_type}/history?authKey={self.api_key}&maxCount=20"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        results = {}
        for entry in data.get("values", []):
            year = entry.get("y")
            quarter = entry.get("p")
            value = entry.get("v")

            if year is None or value is None:
                continue

            if report_type == "year":
                period_key = str(year)
            elif report_type in ("quarter", "r12"):
                if quarter is not None:
                    period_key = f"{year}Q{quarter}"
                else:
                    period_key = str(year)  # fallback
            else:
                period_key = str(year)

            results[period_key] = value

        return results
