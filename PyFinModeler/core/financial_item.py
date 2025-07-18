# PyFinModeler/core/financial_item.py

from typing import Dict, Optional
from .financial_item_type import FinancialItemType
from ..utils.name_sanitizer import sanitize_item_name

class FinancialItem:
    def __init__(self, name: str, item_type: FinancialItemType, historical: Optional[Dict[str, float]] = None, forecasted: Optional[Dict[str, float]] = None):
        self.name = sanitize_item_name(name)
        self.item_type = item_type
        # Sort historical and forecasted data during initialization
        self.historical = dict(sorted(historical.items())) if historical else {}
        self.forecasted = dict(sorted(forecasted.items())) if forecasted else {}

    def add_historical(self, period: str, value: float) -> None:
        self.historical[period] = value
        # Sort the historical data by period
        self.historical = dict(sorted(self.historical.items()))

    def add_forecasted(self, period: str, value: float) -> None:
        self.forecasted[period] = value
        # Sort the forecasted data by period
        self.forecasted = dict(sorted(self.forecasted.items()))

    def get_value(self, period: str) -> Optional[float]:
        return self.forecasted.get(period) or self.historical.get(period)

    def forecast_growth(self, growth_rate: Optional[float] = None, growth_schedule: Optional[Dict[str, float]] = None, periods: int = 5, frequency: str = "Annual") -> None:
        if not self.historical:
            raise ValueError(f"No historical data for {self.name}.")

        last_period = sorted(self.historical.keys())[-1]
        last_value = self.historical[last_period]
        current_value = last_value

        for i in range(1, periods + 1):
            if frequency == "Annual":
                next_period = str(int(last_period[:4]) + i)
            else:
                raise NotImplementedError("Only Annual supported currently.")

            growth = None
            if growth_schedule and next_period in growth_schedule:
                growth = growth_schedule[next_period]
            elif growth_rate is not None:
                growth = growth_rate
            else:
                raise ValueError("No growth specified.")

            current_value *= (1 + growth)
            self.forecasted[next_period] = current_value

    def get_sorted_historical(self) -> Dict[str, float]:
        """Retrieve historical data sorted by period."""
        return dict(sorted(self.historical.items()))

    def get_sorted_forecasted(self) -> Dict[str, float]:
        """Retrieve forecasted data sorted by period."""
        return dict(sorted(self.forecasted.items()))

    def get_all_data_sorted(self) -> Dict[str, float]:
        """Retrieve all data (historical and forecasted) sorted by period."""
        combined_data = {**self.historical, **self.forecasted}
        return dict(sorted(combined_data.items()))
