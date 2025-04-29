# PyFinModeler/data/borsdata_collector.py

import requests
import base64
from typing import Optional, List
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
        self.session = requests.Session()

        # Börsdata authentication
        auth_string = f"{self.api_key}:"
        auth_base64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        self.session.headers.update({
            "Authorization": f"Basic {auth_base64}"
        })

    def fetch_company_by_name(
        self,
        name: str,
        report_type: str = "year",  # 'year', 'r12', 'quarter'
        max_count: int = 5
    ) -> Optional[Company]:
        """
        Fetch company financials by partial name match.

        Args:
            name: Company name (partial match allowed)
            report_type: 'year', 'r12', 'quarter'
            max_count: Number of historical periods to fetch

        Returns:
            Company object with populated Income, Balance, Cash Flow statements
        """
        companies = self.get_all_companies()
        matching = [c for c in companies if name.lower() in c["name"].lower()]

        if not matching:
            print(f"No company found matching {name}")
            return None

        company_info = matching[0]
        company_id = company_info["insId"]

        company = Company(
            name=company_info["name"],
            ticker=company_info["ticker"],
            currency=company_info.get("currency", "SEK")
        )

        self._populate_financials(company, company_id, report_type, max_count)

        return company, company_id, company_info

    def get_all_companies(self) -> List[dict]:
        """
        Fetch all companies from Börsdata.

        Returns:
            List of companies
        """
        url = f"{self.BASE_URL}/instruments?authKey={self.api_key}"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("instruments", [])

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
                company.other_financial_items.add_item(financial_item)

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
        url = f"{self.BASE_URL}/instruments/{company_id}/reports/{report_type}?authKey={self.api_key}&maxCount={max_count}&original=0"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
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
