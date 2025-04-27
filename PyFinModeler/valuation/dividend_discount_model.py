# PyFinModeler/valuation/dividend_discount_model.py

from ..core.company import Company

class DividendDiscountModel:
    def __init__(
        self,
        company: Company,
        base_item_for_dividends: str = "Net Income",
        discount_rate: float = 0.08,
        payout_ratio: float = 0.5,
        terminal_growth_rate: float = 0.02,
        periods: int = 5
    ):
        """
        Initialize Dividend Discount Model.

        Args:
            company: Company object
            base_item_for_dividends: FinancialItem to apply payout ratio to (e.g., 'Net Income', 'profit_To_Equity_Holders', 'free_Cash_Flow')
            discount_rate: Required return (cost of equity)
            payout_ratio: % of earnings (or other base) paid out as dividends
            terminal_growth_rate: Growth rate after forecast horizon
            periods: Number of forecast periods
        """
        self.company = company
        self.base_item_for_dividends = base_item_for_dividends
        self.discount_rate = discount_rate
        self.payout_ratio = payout_ratio
        self.terminal_growth_rate = terminal_growth_rate
        self.periods = periods

    def calculate_value(self) -> float:
        """
        Calculate intrinsic total equity value based on forecasted dividends.
        """
        base_item = self._find_item(self.base_item_for_dividends)

        if not base_item:
            raise ValueError(f"Base item '{self.base_item_for_dividends}' not found for dividend calculation.")

        forecasted_periods = list(base_item.forecasted.keys())
        forecasted_dividends = {}

        # Step 1: Project Dividends
        for period in forecasted_periods[:self.periods]:
            base_value = base_item.forecasted.get(period)
            if base_value is not None:
                dividend = base_value * self.payout_ratio
                forecasted_dividends[period] = dividend

        # Step 2: Discount Dividends
        present_value = 0.0
        for i, (period, dividend) in enumerate(forecasted_dividends.items(), start=1):
            present_value += dividend / ((1 + self.discount_rate) ** i)

        # Step 3: Terminal Value
        final_year = forecasted_periods[min(self.periods, len(forecasted_periods)) - 1]
        final_base_value = base_item.forecasted.get(final_year, 0)
        final_dividend = final_base_value * self.payout_ratio

        terminal_value = (final_dividend * (1 + self.terminal_growth_rate)) / (self.discount_rate - self.terminal_growth_rate)
        terminal_pv = terminal_value / ((1 + self.discount_rate) ** self.periods)

        # Step 4: Total Value
        return present_value + terminal_pv

    def calculate_intrinsic_per_share(self, shares_outstanding: float) -> float:
        """
        Calculate intrinsic value per share.

        Args:
            shares_outstanding: Total number of shares

        Returns:
            Intrinsic value per share
        """
        total_value = self.calculate_value()
        return total_value / shares_outstanding

    def _find_item(self, item_name: str):
        """
        Find a FinancialItem by name across income statement, balance sheet, and cash flow statement.
        """
        return (
            self.company.income_statement.get_item(item_name)
            or self.company.balance_sheet.get_item(item_name)
            or self.company.cash_flow_statement.get_item(item_name)
        )
