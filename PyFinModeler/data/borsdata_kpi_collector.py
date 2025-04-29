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
    ) -> Dict[int, float]:
        """
        Fetch historical KPI values for a specific instrument.

        Args:
            instrument_id: Company Instrument ID (e.g., 1605 for Atlas Copco B)
            kpi_id: KPI ID
            report_type: 'year', 'r12', 'quarter'
            price_type: 'mean', 'low', 'high'

        Returns:
            Dictionary mapping {year: KPI value}
        """

        url = f"{self.BASE_URL}/instruments/{instrument_id}/kpis/{kpi_id}/{report_type}/{price_type}/history?authKey={self.api_key}"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        results = {}
        for entry in data.get("values", []):
            year = entry.get("y")
            value = entry.get("v")
            if year is not None and value is not None:
                results[year] = value

        return results
