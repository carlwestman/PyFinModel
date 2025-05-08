# PyFinModeler/core/company.py

import json
import pandas as pd
from ..kpi.kpi_manager import KPIManager
from .financial_statement import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    KPIStatement,
    OtherFinancialsStatement,
)
from .financial_item import FinancialItem
from .financial_item_type import FinancialItemType

class Company:
    def __init__(self, name: str, ticker: str, currency: str, description: str = None):
        self.name = name
        self.ticker = ticker
        self.currency = currency
        self.description = description  # New description field
        self.income_statement = IncomeStatement()
        self.balance_sheet = BalanceSheet()
        self.cash_flow_statement = CashFlowStatement()
        self.kpi_statement = KPIStatement()  # New KPI Statement
        self.other_financials_statement = OtherFinancialsStatement()
        self.kpi_manager = KPIManager(self)  # Attach KPI manager

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
            "description": self.description,  # Include description in serialization
            "financials": {
                "income_statement": self._statement_to_dict(self.income_statement),
                "balance_sheet": self._statement_to_dict(self.balance_sheet),
                "cash_flow_statement": self._statement_to_dict(self.cash_flow_statement),
                "kpi_statement": self._statement_to_dict(self.kpi_statement),
                "other_financials_statement": self._statement_to_dict(self.other_financials_statement),
            },
        }

    def _statement_to_dict(self, statement) -> dict:
        return {
            item_name: {
                "type": item.item_type.value,
                "historical": dict(sorted(item.historical.items())),  # Sort historical data
                "forecasted": dict(sorted(item.forecasted.items())),  # Sort forecasted data
            }
            for item_name, item in statement.items.items()
        }

    def _load_from_dict(self, data: dict) -> None:
        self.name = data["name"]
        self.ticker = data["ticker"]
        self.currency = data["currency"]
        self.description = data.get("description")  # Load description

        for item_name, item_data in data["financials"]["income_statement"].items():
            item = FinancialItem(
                name=item_name, item_type=FinancialItemType(item_data["type"])
            )
            item.historical = item_data.get("historical", {})
            item.forecasted = item_data.get("forecasted", {})
            self.income_statement.add_item(item)

    def get_statement_summary(self) -> dict:
        """
        Returns a summary of the financial statements and the names of the items they contain.

        Returns:
            A dictionary where the keys are the names of the financial statements
            and the values are lists of item names in each statement.
        """
        return {
            "income_statement": list(self.income_statement.items.keys()),
            "balance_sheet": list(self.balance_sheet.items.keys()),
            "cash_flow_statement": list(self.cash_flow_statement.items.keys()),
            "kpi_statement": list(self.kpi_statement.items.keys()),
            "other_financials_statement": list(self.other_financials_statement.items.keys()),
        }

    def get_statement_as_dataframe(self, statement_name: str) -> pd.DataFrame:
        """
        Returns a pandas DataFrame representation of the specified financial statement.

        Args:
            statement_name: The name of the financial statement (e.g., "income_statement", "balance_sheet", "kpi_statement").

        Returns:
            A pandas DataFrame containing the historical and forecasted data for the specified statement.

        Raises:
            ValueError: If the specified statement name is invalid.
        """
        # Map statement names to their corresponding attributes
        statement_mapping = {
            "income_statement": self.income_statement,
            "balance_sheet": self.balance_sheet,
            "cash_flow_statement": self.cash_flow_statement,
            "kpi_statement": self.kpi_statement,
            "other_financials_statement": self.other_financials_statement,
        }

        # Validate the statement name
        if statement_name not in statement_mapping:
            raise ValueError(f"Invalid statement name: {statement_name}. Valid options are: {list(statement_mapping.keys())}")

        # Get the statement object
        statement = statement_mapping[statement_name]

        # Prepare data for the DataFrame
        data = []
        for item_name, item in statement.items.items():
            row = {"Item": item_name}
            row.update(item.historical)  # Add historical data
            row.update({f"Forecasted_{k}": v for k, v in item.forecasted.items()})  # Add forecasted data
            data.append(row)

        # Create the DataFrame
        df = pd.DataFrame(data)
        df.set_index("Item", inplace=True)  # Set the item name as the index

        # Sort columns by year and quarter (ascending order)
        def sort_key(col):
            if col.startswith("Forecasted_"):
                return float('inf')  # Place forecasted columns at the end
            if "Q" in col:  # Handle quarterly data
                year, quarter = col.split("Q")
                return int(year) * 10 + int(quarter)  # Sort by year and quarter
            return int(col)  # Handle yearly data

        sorted_columns = sorted(df.columns, key=sort_key)
        df = df[sorted_columns]

        return df
