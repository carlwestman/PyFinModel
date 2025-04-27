# PyFinModeler/core/company.py

import json
from ..kpi.kpi_manager import KPIManager
from .financial_statement import IncomeStatement, BalanceSheet, CashFlowStatement
from .financial_item import FinancialItem
from .financial_item_type import FinancialItemType

class Company:
    def __init__(self, name: str, ticker: str, currency: str):
        self.name = name
        self.ticker = ticker
        self.currency = currency
        self.income_statement = IncomeStatement()
        self.balance_sheet = BalanceSheet()
        self.cash_flow_statement = CashFlowStatement()
        self.kpi_manager = KPIManager(self)  # 🚀 New: KPI manager attached automatically

    def save_to_json(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load_from_json(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._load_from_dict(data)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "ticker": self.ticker,
            "currency": self.currency,
            "financials": {
                "income_statement": self._statement_to_dict(self.income_statement),
                "balance_sheet": self._statement_to_dict(self.balance_sheet),
                "cash_flow_statement": self._statement_to_dict(self.cash_flow_statement)
            }
        }

    def _statement_to_dict(self, statement) -> dict:
        return {item_name: {
            "type": item.item_type.value,
            "historical": item.historical,
            "forecasted": item.forecasted
        } for item_name, item in statement.items.items()}

    def _load_from_dict(self, data: dict) -> None:
        self.name = data["name"]
        self.ticker = data["ticker"]
        self.currency = data["currency"]

        for item_name, item_data in data["financials"]["income_statement"].items():
            item = FinancialItem(name=item_name, item_type=FinancialItemType(item_data["type"]))
            item.historical = item_data.get("historical", {})
            item.forecasted = item_data.get("forecasted", {})
            self.income_statement.add_item(item)
