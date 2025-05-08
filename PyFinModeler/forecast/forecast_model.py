# PyFinModeler/forecast/forecast_model.py

from typing import List, Optional
from ..core.company import Company
from .assumption_set import AssumptionSet
from .forecast_rule import ForecastRule
from ..core.financial_item import FinancialItem
from ..kpi.kpi_manager import KPIManager  # Updated import path
from .statistical_forecaster import StatisticalForecaster

class ForecastModel:
    """
    The ForecastModel class is responsible for applying forecast rules to financial items
    and generating forecasts for specified periods.

    Attributes:
        company (Company): The company object containing financial statements.
        assumptions (AssumptionSet): Assumptions used for forecasting.
        periods (int): Number of periods to forecast.
        frequency (str): Frequency of the forecast ('Annual' or 'Quarterly').
        rules (List[ForecastRule]): List of forecast rules to apply.
        kpi_manager (KPIManager): Manager for KPIs used in forecasting.
    """

    def __init__(
        self,
        company: Company,
        assumptions: AssumptionSet,
        periods: int = 5,
        frequency: str = "Annual"
    ):
        """
        Initialize the ForecastModel.

        Args:
            company (Company): The company object containing financial statements.
            assumptions (AssumptionSet): Assumptions used for forecasting.
            periods (int): Number of periods to forecast. Defaults to 5.
            frequency (str): Frequency of the forecast ('Annual' or 'Quarterly'). Defaults to 'Annual'.
        """
        self.company = company
        self.assumptions = assumptions
        self.periods = periods
        self.frequency = frequency
        self.rules: List[ForecastRule] = []
        self.kpi_manager = KPIManager(company)

    def add_forecast_rule(self, rule: ForecastRule) -> None:
        """
        Add a forecast rule to the model.

        Args:
            rule (ForecastRule): The forecast rule to add.

        Example:
            rule = ForecastRule(
                item_name="Revenue",
                method="statistical",
                params={
                    "method": "sarima",
                    "periods": 4,
                    "order": (1, 1, 1),
                    "seasonal_order": (1, 1, 1, 4),
                    "trend": "c",
                    "frequency": "quarter",
                },
                period_range={"start": 1, "end": 4},
            )
            forecast_model.add_forecast_rule(rule)
        """
        self.rules.append(rule)

    def add_kpi(self, kpi_name: str, formula: str) -> None:
        """
        Define a KPI inside the model.

        Args:
            kpi_name (str): The name of the KPI.
            formula (str): The formula for calculating the KPI.

        Example:
            forecast_model.add_kpi("NetProfitMargin", "(NetProfit / Revenue) * 100")
        """
        self.kpi_manager.add_kpi(kpi_name, formula)

    def run_forecast(self) -> None:
        """
        Run the forecast by applying all the forecast rules sequentially.

        Example:
            forecast_model.run_forecast()
        """
        for rule in self.rules:
            self._apply_rule(rule)

    def _apply_rule(self, rule: ForecastRule) -> None:
        """
        Apply a forecast rule to a financial item.

        Args:
            rule (ForecastRule): The forecast rule to apply.

        Raises:
            ValueError: If the financial item or method is not found.

        Example:
            rule = ForecastRule(
                item_name="Revenue",
                method="statistical",
                params={
                    "method": "normal",
                    "periods": 8,
                    "mode": "mean",
                    "std_multiplier": 1.0,
                    "trend": 0.02,
                    "frequency": "quarter",
                },
                period_range={"start": 5, "end": 12},
            )
            forecast_model._apply_rule(rule)
        """
        item = self._find_item(rule.item_name)
        if not item:
            raise ValueError(f"FinancialItem '{rule.item_name}' not found.")

        # Determine the range of periods to apply the rule
        start_period = rule.period_range.get("start", 1)
        end_period = rule.period_range.get("end", self.periods)

        # Generate applicable periods based on the period range
        applicable_periods = []
        last_historical_period = sorted(item.historical.keys())[-1]
        current_year, current_q = self._parse_period(last_historical_period)

        for i in range(1, end_period + 1):
            current_q += 1
            if current_q > 4:
                current_q = 1
                current_year += 1
            period = f"{current_year}Q{current_q}" if "Q" in last_historical_period else str(current_year)
            if start_period <= i <= end_period:
                applicable_periods.append(period)

        if rule.method == "statistical":
            forecaster = StatisticalForecaster({**item.historical, **item.forecasted})

            # Map statistical methods to their corresponding functions
            statistical_methods = {
                "normal": forecaster.forecast_normal,
                "holt_winters": forecaster.forecast_holt_winters,
                "sarima": forecaster.forecast_sarima,
                "prophet": forecaster.forecast_prophet,
            }

            # Get the statistical method from params
            statistical_method = rule.params.get("method", "normal")
            if statistical_method not in statistical_methods:
                raise ValueError(f"Unknown statistical method '{statistical_method}'.")

            # Filter params to remove the "method" key
            method_params = {key: value for key, value in rule.params.items() if key != "method"}

            # Call the selected statistical method
            forecasted = statistical_methods[statistical_method](**method_params)

            # Add forecasted values to the item for the applicable periods
            for period, value in forecasted.items():
                if period in applicable_periods:
                    item.add_forecasted(period, value)

        # Handle other methods (growth_rate, margin_of, etc.)
        elif rule.method == "growth_rate":
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
                    if period in applicable_periods:
                        item.add_forecasted(period, base_value * margin)

        elif rule.method == "fixed":
            fixed_value = rule.params["value"]
            for period in applicable_periods:
                item.add_forecasted(period, fixed_value)

        elif rule.method == "link_to_item":
            source_item_name = rule.params["source_item"]
            rate = rule.params["rate"]
            source_item = self._find_item(source_item_name)
            if source_item:
                for period, source_value in source_item.forecasted.items():
                    if period in applicable_periods:
                        item.add_forecasted(period, source_value * rate)

        elif rule.method == "custom_function":
            if rule.custom_function:
                rule.custom_function(item, self)
            else:
                raise ValueError("Custom function missing.")

        else:
            raise ValueError(f"Unknown method '{rule.method}'.")

    def _parse_period(self, period: str) -> tuple:
        """
        Parse a period string into year and quarter (if applicable).

        Args:
            period: A string in the format 'YYYY' or 'YYYYQ#'.

        Returns:
            A tuple (year, quarter), where quarter is 0 if not applicable.

        Example:
            _parse_period("2024Q1") -> (2024, 1)
            _parse_period("2024") -> (2024, 0)
        """
        if "Q" in period:
            year, quarter = period.split("Q")
            return int(year), int(quarter)
        return int(period), 0

    def _find_item(self, name: str) -> Optional[FinancialItem]:
        """
        Find a financial item by name in the company's financial statements.

        Args:
            name (str): The name of the financial item.

        Returns:
            FinancialItem or None: The financial item if found, otherwise None.

        Example:
            item = forecast_model._find_item("Revenue")
        """
        return (
            self.company.income_statement.get_item(name)
            or self.company.balance_sheet.get_item(name)
            or self.company.cash_flow_statement.get_item(name)
            or self.company.kpi_statement.get_item(name)  # Added KPI Statement
            or self.company.other_financials_statement.get_item(name)
        )
