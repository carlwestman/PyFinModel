# PyFinModeler/visualization/chart_generator.py

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional
from ..core.company import Company
from ..core.financial_item import FinancialItem
from ..kpi.kpi_manager import KPIManager  # Updated import
from scipy.stats import linregress

class ChartGenerator:
    def __init__(self, company: Company):
        """
        Initialize the ChartGenerator.

        Args:
            company (Company): The company object containing financial data.
        """
        self.company = company

    def plot_financial_item(self, item_name: str, save_path: Optional[str] = None) -> None:
        """
        Plot a single FinancialItem's historical and forecasted data.

        Args:
            item_name (str): The name of the FinancialItem to plot.
            save_path (Optional[str]): Path to save the chart. If None, the chart is displayed.

        Raises:
            ValueError: If the specified FinancialItem is not found.

        Example:
            >>> chart_generator.plot_financial_item("Revenue")
        """
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
        """
        Plot multiple FinancialItems as a grouped bar chart.

        Args:
            item_names (List[str]): A list of FinancialItem names to plot.
            save_path (Optional[str]): Path to save the chart. If None, the chart is displayed.

        Raises:
            ValueError: If one or more FinancialItems are not found.

        Example:
            >>> chart_generator.plot_multiple_items_bar(["Revenue", "Expenses"])
        """
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
        """
        Plot multiple FinancialItems as a line chart.

        Args:
            item_names (List[str]): A list of FinancialItem names to plot.
            save_path (Optional[str]): Path to save the chart. If None, the chart is displayed.

        Raises:
            ValueError: If one or more FinancialItems are not found.

        Example:
            >>> chart_generator.plot_multiple_items_line(["Revenue", "NetProfit"])
        """
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

    def plot_kpi(self, kpi_name: str, save_path: Optional[str] = None) -> None:
        """
        Plot a KPI over time.

        Args:
            kpi_name (str): The name of the KPI to plot.
            save_path (Optional[str]): Path to save the chart. If None, the chart is displayed.

        Raises:
            ValueError: If the specified KPI is not defined in the KPIManager.

        Example:
            >>> chart_generator.plot_kpi("NetProfitMargin")
        """
        kpi_manager = self.company.kpi_manager  # Access KPIManager from the company object
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

    def plot_forecast_with_confidence(
        self,
        item_name: str,
        std_multiplier: float = 1.0,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
    ) -> None:
        """
        Plot forecasted data with ± standard deviation confidence bands.

        Args:
            item_name (str): The name of the FinancialItem to plot.
            std_multiplier (float): The width of the confidence band (e.g., 1.0 = ±1σ).
            title (Optional[str]): The title of the plot. If None, a default title is used.
            save_path (Optional[str]): Path to save the chart. If None, the chart is displayed.

        Raises:
            ValueError: If the specified FinancialItem is not found.

        Example:
            >>> chart_generator.plot_forecast_with_confidence("Revenue", std_multiplier=1.5)
        """
        item = self._find_item(item_name)
        if not item:
            raise ValueError(f"Item '{item_name}' not found in company.")

        historical = item.historical
        forecast = item.forecasted

        # Compute stats from historical
        values = list(historical.values())
        mean = np.mean(values)
        std = np.std(values)

        # Build clean period/value lists
        historical_periods = sorted(historical.keys())
        forecast_periods = sorted(forecast.keys())
        forecast_values = [forecast[p] for p in forecast_periods]

        # Confidence bands
        upper_band = [v + std_multiplier * std for v in forecast_values]
        lower_band = [v - std_multiplier * std for v in forecast_values]

        # Plotting
        plt.figure(figsize=(12, 6))
        plt.plot(historical_periods, [historical[p] for p in historical_periods], label="Historical", marker='o', color='blue')
        plt.plot(forecast_periods, forecast_values, label="Forecast", marker='o', color='orange')

        plt.fill_between(forecast_periods, lower_band, upper_band, color='orange', alpha=0.2, label=f"±{std_multiplier}σ Confidence")

        plt.xticks(rotation=45)
        plt.title(title or f"{item_name} Forecast with ±{std_multiplier}σ Band")
        plt.xlabel("Period")
        plt.ylabel("Value")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
    
        if save_path:
            plt.savefig(save_path)
            print(f"KPI chart saved to {save_path}")
        else:
            plt.show()
                
        plt.close()

    def plot_scatter_with_regression(
        self,
        x_item_name: str,
        y_item_name: str,
        save_path: Optional[str] = None,
    ) -> None:
        """
        Create a scatterplot of two financial items with a least squares linear regression line.

        Args:
            x_item_name (str): The name of the FinancialItem to use for the x-axis.
            y_item_name (str): The name of the FinancialItem to use for the y-axis.
            save_path (Optional[str]): Path to save the chart. If None, the chart is displayed.

        Raises:
            ValueError: If one or both FinancialItems are not found or have no overlapping periods.

        Example:
            >>> chart_generator.plot_scatter_with_regression("Revenue", "NetProfit")
        """
        # Find the financial items
        x_item = self._find_item(x_item_name)
        y_item = self._find_item(y_item_name)

        if not x_item or not y_item:
            raise ValueError(f"One or both items '{x_item_name}' and '{y_item_name}' not found.")

        # Find overlapping periods
        x_data = {period: value for period, value in x_item.historical.items() if value is not None}
        y_data = {period: value for period, value in y_item.historical.items() if value is not None}
        common_periods = sorted(set(x_data.keys()).intersection(y_data.keys()))

        if not common_periods:
            raise ValueError(f"No overlapping periods found between '{x_item_name}' and '{y_item_name}'.")

        # Extract data for the common periods
        x_values = np.array([x_data[period] for period in common_periods])
        y_values = np.array([y_data[period] for period in common_periods])

        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = linregress(x_values, y_values)

        # Generate regression line
        regression_line = slope * x_values + intercept

        # Plot scatterplot and regression line
        plt.figure(figsize=(10, 6))
        plt.scatter(x_values, y_values, label="Data Points", color="blue", alpha=0.7)
        plt.plot(x_values, regression_line, label=f"y = {slope:.2f}x + {intercept:.2f}", color="red")

        # Add chart details
        plt.title(f"Scatterplot of {x_item_name} vs {y_item_name}")
        plt.xlabel(x_item_name)
        plt.ylabel(y_item_name)
        plt.legend()
        plt.grid(True)

        # Display R-squared value
        plt.text(
            0.05, 0.95,
            f"$R^2$ = {r_value**2:.2f}",
            transform=plt.gca().transAxes,
            fontsize=12,
            verticalalignment="top",
        )

        # Save or show the chart
        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        else:
            plt.show()

        plt.close()

    def _find_item(self, item_name: str) -> FinancialItem:
        """
        Locate a FinancialItem in the company's financial statements.

        Args:
            item_name (str): The name of the FinancialItem to locate.

        Returns:
            FinancialItem: The located FinancialItem object, or None if not found.

        Example:
            >>> item = chart_generator._find_item("Revenue")
        """
        return (
            self.company.income_statement.get_item(item_name)
            or self.company.balance_sheet.get_item(item_name)
            or self.company.cash_flow_statement.get_item(item_name)
            or self.company.kpi_statement.get_item(item_name)
            or self.company.other_financials_statement.get_item(item_name)
        )
