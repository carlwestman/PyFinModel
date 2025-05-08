# PyFinModeler/core/financial_statement.py

from abc import ABC, abstractmethod
from typing import Dict, Optional
from .financial_item import FinancialItem
import matplotlib.pyplot as plt

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

    def plot(
        self,
        type: str = "line",
        include: Optional[list] = None,
        exclude: Optional[list] = None,
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot the financial statement as a line or bar chart.

        Args:
            type (str): The type of plot ('line' or 'bar'). Defaults to 'line'.
            include (Optional[list]): List of item names to include in the plot. Defaults to None (include all).
            exclude (Optional[list]): List of item names to exclude from the plot. Defaults to None.
            save_path (Optional[str]): Path to save the chart. If None, the chart is displayed.

        Raises:
            ValueError: If the specified plot type is invalid.
        """
        if type not in ["line", "bar"]:
            raise ValueError("Invalid plot type. Supported types are 'line' and 'bar'.")

        # Filter items based on include and exclude
        items_to_plot = self.items.values()
        if include:
            items_to_plot = [item for item in items_to_plot if item.name in include]
        if exclude:
            items_to_plot = [item for item in items_to_plot if item.name not in exclude]

        if not items_to_plot:
            raise ValueError("No items to plot after applying include/exclude filters.")

        # Prepare data for plotting
        periods = sorted(
            set.union(
                *(set(item.historical.keys()).union(item.forecasted.keys()) for item in items_to_plot)
            )
        )
        data = {item.name: [item.get_value(period) or 0 for period in periods] for item in items_to_plot}

        # Plotting
        plt.figure(figsize=(12, 7))
        if type == "line":
            for item_name, values in data.items():
                plt.plot(periods, values, marker="o", label=item_name)
        elif type == "bar":
            bar_width = 0.8 / len(data)
            x = range(len(periods))
            for idx, (item_name, values) in enumerate(data.items()):
                plt.bar(
                    [p + idx * bar_width for p in x],
                    values,
                    width=bar_width,
                    label=item_name,
                )
            plt.xticks([p + bar_width * (len(data) - 1) / 2 for p in x], periods)

        # Chart formatting
        plt.title(f"{self.statement_name} - {type.capitalize()} Chart")
        plt.xlabel("Period")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save or show the plot
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        else:
            plt.show()

        plt.close()

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

class KPIStatement(FinancialStatement):
    def __init__(self):
        super().__init__("KPI Statement")

    def validate(self) -> bool:
        return True

class OtherFinancialsStatement(FinancialStatement):
    def __init__(self):
        super().__init__("Other Financials Statement")

    def validate(self) -> bool:
        return True
