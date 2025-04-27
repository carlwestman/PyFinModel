# PyFinModeler/visualization/chart_generator.py

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional
from ..core.company import Company
from ..core.financial_item import FinancialItem
from ..kpi.kpi_manager import KPIManager  # Updated import

class ChartGenerator:
    def __init__(self, company: Company):
        self.company = company

    def plot_financial_item(self, item_name: str, save_path: Optional[str] = None) -> None:
        """Plot a single FinancialItem."""
        item = self._find_item(item_name)
        if not item:
            raise ValueError(f"Item '{item_name}' not found.")

        periods = sorted(set(item.historical.keys()).union(item.forecasted.keys()))
        values = [item.get_value(period) or 0 for period in periods]

        plt.figure(figsize=(10, 6))
        plt.plot(periods, values, marker="o", label=item_name)
        plt.title(f"{item_name} - Historical and Forecasted")
        plt.xlabel("Period")
        plt.ylabel("Amount")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        else:
            plt.show()

        plt.close()

    def plot_multiple_items_bar(self, item_names: List[str], save_path: Optional[str] = None) -> None:
        """Plot multiple FinancialItems as grouped bar chart."""
        items = [self._find_item(name) for name in item_names]
        if not all(items):
            raise ValueError("One or more items not found.")

        periods = sorted(set.union(*(set(item.historical.keys()).union(item.forecasted.keys()) for item in items)))
        n_periods = len(periods)
        n_items = len(items)

        bar_width = 0.8 / n_items
        x = np.arange(n_periods)

        plt.figure(figsize=(12, 7))

        for idx, item in enumerate(items):
            values = [item.get_value(period) or 0 for period in periods]
            plt.bar(x + idx * bar_width, values, width=bar_width, label=item.name)

        plt.title("Financial Items Comparison")
        plt.xlabel("Period")
        plt.ylabel("Amount")
        plt.xticks(x + bar_width * (n_items-1)/2, periods, rotation=45)
        plt.legend()
        plt.grid(axis='y')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        else:
            plt.show()

        plt.close()

    def plot_multiple_items_line(self, item_names: List[str], save_path: Optional[str] = None) -> None:
        """Plot multiple FinancialItems as line chart."""
        items = [self._find_item(name) for name in item_names]
        if not all(items):
            raise ValueError("One or more items not found.")

        periods = sorted(set.union(*(set(item.historical.keys()).union(item.forecasted.keys()) for item in items)))

        plt.figure(figsize=(12, 7))

        for item in items:
            values = [item.get_value(period) or 0 for period in periods]
            plt.plot(periods, values, marker="o", label=item.name)

        plt.title("Financial Items Trends")
        plt.xlabel("Period")
        plt.ylabel("Amount")
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        else:
            plt.show()

        plt.close()

    def plot_kpi(self, kpi_manager: KPIManager, kpi_name: str, save_path: Optional[str] = None) -> None:
        """Plot a KPI over time."""
        kpi_results = kpi_manager.calculate_kpi(kpi_name)

        periods = sorted(kpi_results.keys())
        values = [kpi_results[period] for period in periods]

        plt.figure(figsize=(10, 6))
        plt.plot(periods, values, marker="o", label=kpi_name)
        plt.title(f"{kpi_name} Over Time")
        plt.xlabel("Period")
        plt.ylabel("KPI Value")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"KPI chart saved to {save_path}")
        else:
            plt.show()

        plt.close()

    def _find_item(self, item_name: str) -> FinancialItem:
        """Locate a FinancialItem."""
        return (
            self.company.income_statement.get_item(item_name)
            or self.company.balance_sheet.get_item(item_name)
            or self.company.cash_flow_statement.get_item(item_name)
        )
