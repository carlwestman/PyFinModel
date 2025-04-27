# PyFinModeler/data/borsdata_kpi_collector.py

import requests
import base64
from typing import Dict

class BorsdataKPICollector:
    BASE_URL = "https://apiservice.borsdata.se/v1"

    def __init__(self, api_key: str):
        """
        Initializes the KPI collector to fetch global KPIs from Börsdata.

        Args:
            api_key: Your personal Börsdata API key
        """
        self.api_key = api_key
        self.session = requests.Session()

        # Börsdata authentication: Basic Auth (username=api_key, password=empty)
        auth_string = f"{self.api_key}:"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        self.session.headers.update({
            "Authorization": f"Basic {auth_base64}"
        })

    def fetch_kpis(
        self,
        kpi_id: int,
        period_type: str = "1year",   # ✅ Correct parameter: 1year, 3year, 5year
        calculation: str = "mean"      # mean, low, high
    ) -> Dict[int, float]:
        """
        Fetch KPI values for all global instruments.

        Args:
            kpi_id: KPI ID according to Börsdata documentation
            period_type: '1year', '3year', or '5year'
            calculation: 'mean', 'low', or 'high'

        Returns:
            Dictionary mapping Instrument ID -> KPI value
        """
        url = f"{self.BASE_URL}/instruments/global/kpis/{kpi_id}/{period_type}/{calculation}?authKey={self.api_key}"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        results = {}
        for entry in data.get("values", []):
            instrument_id = entry.get("i")
            value = entry.get("n")
            if instrument_id is not None and value is not None:
                results[instrument_id] = value

        return results
