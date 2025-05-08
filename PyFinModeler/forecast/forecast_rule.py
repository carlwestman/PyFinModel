# PyFinModeler/forecast/forecast_rule.py

from typing import Callable, Dict, Union, Optional

class ForecastRule:
    def __init__(
        self,
        item_name: str,
        method: str,
        params: Optional[Dict[str, Union[float, str, Dict[str, float]]]] = None,
        custom_function: Optional[Callable[[object, object], None]] = None,
        uses_kpi: bool = False,
        period_range: Optional[Dict[str, int]] = None,
    ):
        """
        Represents a rule for forecasting financial items.

        Args:
            item_name (str): The name of the financial item or KPI to forecast.
            method (str): The forecasting method to use. Supported methods:
                - 'growth_rate': Apply a growth rate to forecast values.
                - 'margin_of': Calculate forecast values as a margin of another item.
                - 'fixed': Set forecast values to a fixed value.
                - 'link_to_item': Link forecast values to another item with a scaling factor.
                - 'custom_function': Apply a custom function for forecasting.
            params (Optional[Dict]): Parameters for the forecasting method.
            custom_function (Optional[Callable]): A custom function for forecasting.
            uses_kpi (bool): Whether the rule applies to a KPI instead of a financial item.
            period_range (Optional[Dict]): Range of periods the rule applies to 
                (e.g., {"start": 1, "end": 4}).

        Examples:
            # Example for 'growth_rate'
            rule = ForecastRule(
                item_name="Revenue",
                method="growth_rate",
                params={
                    "rate": 0.05,  # 5% growth rate
                    "schedule": {"2025": 0.03, "2026": 0.02},  # Custom growth rates
                },
                period_range={"start": 1, "end": 5},
            )

            # Example for 'margin_of'
            rule = ForecastRule(
                item_name="Gross_Profit",
                method="margin_of",
                params={
                    "base_item": "Revenue",
                    "margin": 0.3,  # 30% margin
                },
                period_range={"start": 1, "end": 8},
            )

            # Example for 'fixed'
            rule = ForecastRule(
                item_name="Fixed_Expense",
                method="fixed",
                params={
                    "value": 1000.0,  # Fixed value for all periods
                },
                period_range={"start": 1, "end": 12},
            )

            # Example for 'link_to_item'
            rule = ForecastRule(
                item_name="Operating_Expenses",
                method="link_to_item",
                params={
                    "source_item": "Revenue",
                    "rate": 0.8,  # 80% of Revenue
                },
                period_range={"start": 1, "end": 12},
            )

            # Example for 'custom_function'
            rule = ForecastRule(
                item_name="Custom_Item",
                method="custom_function",
                custom_function=lambda item, model: item.add_forecasted("2025", 5000.0),
                period_range={"start": 1, "end": 1},
            )
        """
        self.item_name = item_name
        self.method = method
        self.params = params or {}
        self.custom_function = custom_function
        self.uses_kpi = uses_kpi
        self.period_range = period_range or {"start": 1, "end": None}  # Default: apply to all periods

    def __repr__(self):
        return f"ForecastRule(item_name={self.item_name}, method={self.method}, params={self.params})"
