# PyFinModeler/core/financial_statement.py

from abc import ABC, abstractmethod
from typing import Dict, Optional
from .financial_item import FinancialItem

class FinancialStatement(ABC):
    def __init__(self, statement_name: str):
        self.statement_name = statement_name
        self.items: Dict[str, FinancialItem] = {}

    def add_item(self, item: FinancialItem) -> None:
        self.items[item.name] = item

    def get_item(self, item_name: str) -> Optional[FinancialItem]:
        return self.items.get(item_name)

    @abstractmethod
    def validate(self) -> bool:
        pass

class IncomeStatement(FinancialStatement):
    def __init__(self):
        super().__init__("Income Statement")

    def validate(self) -> bool:
        return True  # Placeholder for future detailed validation

class BalanceSheet(FinancialStatement):
    def __init__(self):
        super().__init__("Balance Sheet")

    def validate(self) -> bool:
        return True

class CashFlowStatement(FinancialStatement):
    def __init__(self):
        super().__init__("Cash Flow Statement")

    def validate(self) -> bool:
        return True
