# PyFinModeler/scenario/scenario_model.py

import copy
from typing import Dict, Optional
from ..core.company import Company
from ..forecast.assumption_set import AssumptionSet
from ..forecast.forecast_model import ForecastModel
from ..valuation.dividend_discount_model import DividendDiscountModel

class ScenarioModel:
    def __init__(
        self,
        company: Company,
        shares_outstanding: float,
        market_price: Optional[float] = None,
        periods: int = 5,
        frequency: str = "Annual",
        payout_ratio: float = 0.5,
        base_item_for_dividends: str = "Net Income",
        terminal_growth_rate: float = 0.02,
        discount_rate: float = 0.08
    ):
        """
        Initialize ScenarioModel.

        Args:
            company: The base Company object to run scenarios on
            shares_outstanding: Total shares
            market_price: Current share price
            periods: Forecast periods
            frequency: Forecast frequency (only 'Annual' supported for now)
            payout_ratio: Dividend payout ratio (fraction, not percentage)
            base_item_for_dividends: Which FinancialItem to apply payout ratio on
            terminal_growth_rate: Growth after forecast horizon
            discount_rate: Cost of equity
        """
        self.company = company
        self.shares_outstanding = shares_outstanding
        self.market_price = market_price
        self.periods = periods
        self.frequency = frequency
        self.payout_ratio = payout_ratio
        self.base_item_for_dividends = base_item_for_dividends
        self.terminal_growth_rate = terminal_growth_rate
        self.discount_rate = discount_rate

    def run_scenario(self, assumptions: AssumptionSet, label: str) -> Dict[str, Optional[float]]:
        """
        Runs a forecast and valuation with custom assumptions.

        Args:
            assumptions: New AssumptionSet for this scenario
            label: Scenario label ("Bull Case", "Base Case", "Bear Case")

        Returns:
            Dictionary with scenario results
        """

        # Step 1: Deep Copy the company
        company_copy = copy.deepcopy(self.company)

        # Step 2: Setup Forecast Model (⚠️ Assumes forecast rules are re-attached externally if needed!)
        forecast_model = ForecastModel(
            company=company_copy,
            assumptions=assumptions,
            periods=self.periods,
            frequency=self.frequency
        )

        # Step 3: Valuation using updated parameters
        ddm_model = DividendDiscountModel(
            company=company_copy,
            base_item_for_dividends=self.base_item_for_dividends,
            discount_rate=self.discount_rate,
            payout_ratio=self.payout_ratio,
            terminal_growth_rate=self.terminal_growth_rate,
            periods=self.periods
        )

        intrinsic_value_total = ddm_model.calculate_value()
        intrinsic_value_per_share = ddm_model.calculate_intrinsic_per_share(self.shares_outstanding)

        margin_of_safety = None
        if self.market_price:
            margin_of_safety = (intrinsic_value_per_share - self.market_price) / self.market_price

        return {
            "Scenario": label,
            "Intrinsic Value Total": intrinsic_value_total,
            "Intrinsic Value Per Share": intrinsic_value_per_share,
            "Margin of Safety": margin_of_safety
        }
