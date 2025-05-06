# PyFinModeler/data/borsdata_collector.py

import requests
import base64
import json
import os
from typing import Optional, List, Dict
from ..core.company import Company
from ..core.financial_item import FinancialItem
from ..core.financial_item_type import FinancialItemType


class BorsdataCollector:
    BASE_URL = "https://apiservice.borsdata.se/v1"

    def __init__(self, api_key: str):
        """
        Initializes the BorsdataCollector.

        Args:
            api_key: Your Börsdata API Key
        """
        self.api_key = api_key
        self.current_company_id = None
        self.session = requests.Session()

        # Börsdata authentication
        auth_string = f"{self.api_key}:"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        self.session.headers.update({
            "Authorization": f"Basic {auth_base64}"
        })

    def fetch_data(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """
        General method to fetch data from Börsdata API.

        Args:
            endpoint: API endpoint (relative to BASE_URL)
            params: Query parameters for the request

        Returns:
            Parsed JSON response as a dictionary

        Raises:
            Exception: If the API response status code is not 200
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)

        if response.status_code != 200:
            error_message = response.json().get("message", "Unknown error")
            raise Exception(f"{response.status_code} Server Error: {error_message}")

        return response.json()

    def get_all_companies(self) -> List[dict]:
        """
        Fetch all companies from Börsdata.

        Returns:
            List of companies
        """
        endpoint = "/instruments"
        params = {"authKey": self.api_key}
        data = self.fetch_data(endpoint, params)
        return data.get("instruments", [])

    def fetch_company_description(self, instrument_id: int) -> Optional[str]:
        """
        Fetch the description of a company using the /instruments/description API endpoint.

        Args:
            instrument_id: The Börsdata instrument ID of the company.

        Returns:
            The description of the company in English, or None if not available.
        """
        endpoint = "/instruments/description"
        params = {
            "authKey": self.api_key,
            "instList": instrument_id
        }
        data = self.fetch_data(endpoint, params)
        descriptions = data.get("list", [])
        for desc in descriptions:
            if desc["insId"] == instrument_id and desc["languageCode"] == "en":
                return desc["text"]
        return None

    def fetch_company(self, name: Optional[str] = None, company_id: Optional[int] = None) -> Optional[Company]:
        """
        Fetch a company by name or company_id and populate its description, financials, and standard KPIs.

        Args:
            name: The name of the company (optional).
            company_id: The Börsdata instrument ID of the company (optional).

        Returns:
            A Company object with its description, financials, and standard KPIs populated, or None if not found.

        Raises:
            ValueError: If neither `name` nor `company_id` is provided.
        """
        if not name and not company_id:
            raise ValueError("Either 'name' or 'company_id' must be provided.")

        companies = self.get_all_companies()
        
        # Fetch company by name
        if name:
            matching = [c for c in companies if name.lower() in c["name"].lower()]
            if not matching:
                return None
            company_info = matching[0]
            company_id = company_info["insId"]
        else:
            # Fetch company by company_id
            matching = [c for c in companies if c["insId"] == company_id]
            if not matching:
                return None
            company_info = matching[0]
        
        # Store the company_id on the object
        self.current_company_id = company_id

        # Fetch description
        description = self.fetch_company_description(company_id)
        
        # Create the Company object
        company = Company(
            name=company_info["name"],
            ticker=company_info["ticker"],
            currency=company_info.get("reportCurrency", "SEK"),
            description=description
        )
        
        # Populate financials
        self._populate_financials(company, company_id, report_type="year", max_count=5)

        # Populate standard KPIs
        standard_kpis = [
            "P/E",
            "EV/EBIT",
            "EV/EBITDA",
            "Bruttomarginal",
            "EBITDA/Marginal",
            "Rorelsemarginal",
            "Vinstmarginal",
            "FCF/Marginal",
            "ROE",
            "ROA",
            "Utdelning/FCF",
            "AntalAktier",
            "Utdelning/Aktie",
            "Direktavkastning",
            "Utdelningsandel"
        ]

        for kpi_name in standard_kpis:
            try:
                # Fetch KPI and automatically add it to the KPIStatement
                self.fetch_kpi_by_name(company, kpi_name)
            except ValueError as e:
                print(f"Warning: Could not fetch KPI '{kpi_name}'. Reason: {e}")

        # Return the company object
        return company

    def _populate_financials(self, company: Company, company_id: int, report_type: str, max_count: int) -> None:
        """
        Fetch Income, Balance, Cash Flow reports and populate company.

        Args:
            company: Company object
            company_id: Börsdata Instrument ID
            report_type: 'year', 'r12', 'quarter'
            max_count: Number of periods
        """
        reports = self._get_reports(company_id, report_type=report_type, max_count=max_count)

        if not reports:
            print(f"No reports found for company ID {company_id}")
            return

        field_type_mapping = self._get_field_type_mapping()

        for field_name in reports[0].keys():
            if field_name in ["year", "period", "report_Date", "report_Start_Date", "report_End_Date",
                              "currency", "currency_Ratio", "broken_Fiscal_Year", "instrument"]:
                continue  # Skip meta fields

            financial_item = FinancialItem(
                name=field_name,
                item_type=field_type_mapping.get(field_name, FinancialItemType.OTHER)
            )

            for report in reports:
                year = str(report["year"])
                value = report.get(field_name)
                if value is not None:
                    financial_item.add_historical(year, value)

            # Attach to the correct statement
            if financial_item.item_type in (FinancialItemType.REVENUE, FinancialItemType.EXPENSE, FinancialItemType.RESULT):
                company.income_statement.add_item(financial_item)
            elif financial_item.item_type in (FinancialItemType.ASSET, FinancialItemType.LIABILITY, FinancialItemType.EQUITY):
                company.balance_sheet.add_item(financial_item)
            elif financial_item.item_type in (FinancialItemType.CASH_FLOW_OPERATING, FinancialItemType.CASH_FLOW_INVESTING,
                                               FinancialItemType.CASH_FLOW_FINANCING, FinancialItemType.CASH_FLOW_SUMMARY):
                company.cash_flow_statement.add_item(financial_item)
            else:
                company.other_financials_statement.add_item(financial_item)

    def _get_reports(self, company_id: int, report_type: str, max_count: int) -> List[dict]:
        """
        Fetch raw financial reports from Börsdata.

        Args:
            company_id: Instrument ID
            report_type: 'year', 'r12', 'quarter'
            max_count: periods back

        Returns:
            List of reports
        """
        endpoint = f"/instruments/{company_id}/reports/{report_type}"
        params = {
            "authKey": self.api_key,
            "maxCount": max_count,
            "original": 0
        }
        data = self.fetch_data(endpoint, params)
        return data.get("reports", [])

    def _get_field_type_mapping(self) -> dict:
        """
        Map Börsdata financial fields to FinancialItemTypes.
        """
        return {
            "revenues": FinancialItemType.REVENUE,
            "net_Sales": FinancialItemType.REVENUE,
            "gross_Income": FinancialItemType.REVENUE,
            "operating_Income": FinancialItemType.REVENUE,
            "profit_Before_Tax": FinancialItemType.RESULT,
            "profit_To_Equity_Holders": FinancialItemType.RESULT,
            "earnings_Per_Share": FinancialItemType.RATIO,
            "dividend": FinancialItemType.DIVIDEND,
            "cash_Flow_From_Operating_Activities": FinancialItemType.CASH_FLOW_OPERATING,
            "cash_Flow_From_Investing_Activities": FinancialItemType.CASH_FLOW_INVESTING,
            "cash_Flow_From_Financing_Activities": FinancialItemType.CASH_FLOW_FINANCING,
            "cash_Flow_For_The_Year": FinancialItemType.CASH_FLOW_SUMMARY,
            "free_Cash_Flow": FinancialItemType.CASH_FLOW_OPERATING,
            "intangible_Assets": FinancialItemType.ASSET,
            "tangible_Assets": FinancialItemType.ASSET,
            "financial_Assets": FinancialItemType.ASSET,
            "non_Current_Assets": FinancialItemType.ASSET,
            "current_Assets": FinancialItemType.ASSET,
            "total_Assets": FinancialItemType.ASSET,
            "cash_And_Equivalents": FinancialItemType.ASSET,
            "non_Current_Liabilities": FinancialItemType.LIABILITY,
            "current_Liabilities": FinancialItemType.LIABILITY,
            "net_Debt": FinancialItemType.LIABILITY,
            "total_Equity": FinancialItemType.EQUITY,
        }

    def fetch_kpi(
        self,
        company: Company,
        kpi_id: int,
        kpi_name: str,
        report_type: str = "year",  # 'year', 'r12', 'quarter'
        price_type: str = "mean"    # 'mean', 'low', 'high'
    ) -> Dict[str, float]:
        """
        Fetch historical KPI values for a specific instrument and store them in the KPIStatement.

        Args:
            company: The Company object to which the KPI belongs.
            kpi_id: KPI ID
            kpi_name: Name of the KPI
            report_type: 'year', 'r12', 'quarter'
            price_type: 'mean', 'low', 'high'

        Returns:
            Dictionary mapping {period: KPI value}, where period is "2024", "2024Q2", etc.
        """
        if not self.current_company_id:
            raise ValueError("No company has been fetched. Please fetch a company first.")

        endpoint = f"/instruments/{self.current_company_id}/kpis/{kpi_id}/{report_type}/{price_type}/history"
        params = {
            "authKey": self.api_key,
            "maxCount": 20
        }
        data = self.fetch_data(endpoint, params)

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

        # Create a FinancialItem for the KPI
        kpi_item = FinancialItem(
            name=kpi_name,
            item_type=FinancialItemType.RATIO,  # Assuming KPIs are ratios; adjust as needed
            historical=results
        )

        # Add the FinancialItem to the KPIStatement of the Company
        company.kpi_statement.add_item(kpi_item)

        return results

    def fetch_kpi_by_name(
        self,
        company: Company,
        kpi_name: str,
        report_type: str = "year",
        price_type: str = "mean"
    ) -> Dict[str, float]:
        """
        Fetch historical KPI values by KPI name, report type, and price type.

        Args:
            company: The Company object to which the KPI belongs.
            kpi_name: The name of the KPI (e.g., "P/E", "P/S").
            report_type: The type of report ('year', 'r12', 'quarter'). Defaults to "year".
            price_type: The price type ('mean', 'low', 'high'). Defaults to "mean".

        Returns:
            Dictionary mapping {period: KPI value}, where period is "2024", "2024Q2", etc.

        Raises:
            ValueError: If the KPI name is not found in the mapping or the specified report_type/price_type is invalid.
        """
        # Get the KPI parameters mapping
        kpi_params_mapping = self._get_kpi_params_mapping()

        # Check if the KPI name exists in the mapping
        if kpi_name not in kpi_params_mapping:
            raise ValueError(f"KPI name '{kpi_name}' not found in the KPI parameters mapping.")

        # Find the matching KPI parameters
        for kpi_params in kpi_params_mapping[kpi_name]:
            if kpi_params["report_type"] == report_type and kpi_params["price_type"] == price_type:
                # Fetch the KPI using the fetch_kpi method
                return self.fetch_kpi(
                    company=company,
                    kpi_id=kpi_params["kpi_id"],
                    kpi_name=kpi_name,
                    report_type=report_type,
                    price_type=price_type
                )

        # If no matching parameters are found, raise an error
        raise ValueError(
            f"No matching KPI parameters found for KPI name '{kpi_name}' with report_type '{report_type}' and price_type '{price_type}'."
        )

    def _get_kpi_params_mapping(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Returns a mapping of KPI names to their respective parameters by loading data from an external JSON file.

        Returns:
            A dictionary where the keys are KPI names and the values are lists of dictionaries
            containing the parameters for each KPI (kpi_id, report_type, price_type, description).
        """
        file_path = os.path.join(os.path.dirname(__file__), "kpi_params.json")
        with open(file_path, "r") as file:
            return json.load(file)

