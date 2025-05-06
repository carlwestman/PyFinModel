# PyFinModeler/forecast/forecast_model.py

from typing import List, Optional
from ..core.company import Company
from .assumption_set import AssumptionSet
from .forecast_rule import ForecastRule
from ..core.financial_item import FinancialItem
from ..kpi.kpi_manager import KPIManager  # Updated import path
from .statistical_forecaster import StatisticalForecaster

class ForecastModel:
    def __init__(
        self,
        company: Company,
        assumptions: AssumptionSet,
        periods: int = 5,
        frequency: str = "Annual"
    ):
        self.company = company
        self.assumptions = assumptions
        self.periods = periods
        self.frequency = frequency
        self.rules: List[ForecastRule] = []
        self.kpi_manager = KPIManager(company)

    def add_forecast_rule(self, rule: ForecastRule) -> None:
        self.rules.append(rule)

    def add_kpi(self, kpi_name: str, formula: str) -> None:
        """Define a KPI inside the model."""
        self.kpi_manager.add_kpi(kpi_name, formula)

    def run_forecast(self) -> None:
        for rule in self.rules:
            self._apply_rule(rule)

    def _apply_rule(self, rule: ForecastRule) -> None:
        if rule.uses_kpi:
            # KPI-based forecasting
            kpi_results = self.kpi_manager.calculate_kpi(rule.item_name)

            base_item_name = rule.params.get("base_item")
            target_item = self._find_item(base_item_name)
            if not target_item:
                raise ValueError(f"Target item '{base_item_name}' not found.")

            adjustment_factor = rule.params.get("adjustment_factor", 1.0)

            for period, kpi_value in kpi_results.items():
                if kpi_value is not None:
                    adjusted_value = kpi_value * adjustment_factor
                    target_item.add_forecasted(period, adjusted_value)

        else:
            # Normal FinancialItem forecast
            item = self._find_item(rule.item_name)
            if not item:
                raise ValueError(f"FinancialItem {rule.item_name} not found.")

            if rule.method == "growth_rate":
                growth_schedule = rule.params.get("schedule")
                growth_rate = rule.params.get("rate")
                item.forecast_growth(
                    growth_rate=growth_rate,
                    growth_schedule=growth_schedule,
                    periods=self.periods,
                    frequency=self.frequency
                )

            elif rule.method == "margin_of":
                base_item_name = rule.params["base_item"]
                margin = rule.params["margin"]
                base_item = self._find_item(base_item_name)
                if base_item:
                    for period, base_value in base_item.forecasted.items():
                        item.add_forecasted(period, base_value * margin)

            elif rule.method == "fixed":
                fixed_value = rule.params["value"]
                for i in range(1, self.periods + 1):
                    if self.frequency == "Annual":
                        year = int(sorted(item.historical.keys())[-1][:4]) + i
                        period = str(year)
                    else:
                        raise NotImplementedError("Quarterly not implemented yet.")
                    item.add_forecasted(period, fixed_value)

            elif rule.method == "link_to_item":
                source_item_name = rule.params["source_item"]
                rate = rule.params["rate"]
                source_item = self._find_item(source_item_name)
                if source_item:
                    for period, source_value in source_item.forecasted.items():
                        item.add_forecasted(period, source_value * rate)

            elif rule.method == "custom_function":
                if rule.custom_function:
                    rule.custom_function(item, self)
                else:
                    raise ValueError("Custom function missing.")
            
            elif rule.method == "statistical":
                item = self._find_item(rule.item_name)
                if not item:
                    raise ValueError(f"FinancialItem '{rule.item_name}' not found.")

                forecaster = StatisticalForecaster(item.historical)
                params = rule.params

                forecasted = forecaster.forecast_normal(
                    periods=self.periods,
                    mode=params.get("mode", "mean"),
                    std_multiplier=params.get("std_multiplier", 1.0),
                    trend=params.get("trend", 0.0),
                    frequency=params.get("frequency", "year"),
                    random_seed=params.get("random_seed")
                )

                for period, value in forecasted.items():
                    item.add_forecasted(period, value)

            else:
                raise ValueError(f"Unknown method '{rule.method}'.")

    def _find_item(self, name: str) -> Optional[FinancialItem]:
        return (
            self.company.income_statement.get_item(name)
            or self.company.balance_sheet.get_item(name)
            or self.company.cash_flow_statement.get_item(name)
            or self.company.kpi_statement.get_item(name)  # Added KPI Statement
            or self.company.other_financials_statement.get_item(name)
        )
