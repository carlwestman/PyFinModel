# PyFinModeler/valuation/valuation_summary_report.py

from typing import Optional, Dict
from .dividend_discount_model import DividendDiscountModel
from ..core.company import Company

class ValuationSummaryReport:
    def __init__(
        self,
        company: Company,
        valuation_model: DividendDiscountModel,
        shares_outstanding: float,
        market_price: Optional[float] = None
    ):
        self.company = company
        self.valuation_model = valuation_model
        self.shares_outstanding = shares_outstanding
        self.market_price = market_price

    def generate(self) -> None:
        """Print valuation summary report."""
        intrinsic_value_total = self.valuation_model.calculate_value()
        intrinsic_value_per_share = self.valuation_model.calculate_intrinsic_per_share(self.shares_outstanding)

        print("="*50)
        print(f"Valuation Summary for {self.company.name} ({self.company.ticker})")
        print("="*50)
        print(f"Currency: {self.company.currency}")
        print(f"Forecast Periods: {self.valuation_model.periods} (Annual)")
        print(f"Payout Ratio: {self.valuation_model.payout_ratio:.1%}")
        print(f"Discount Rate: {self.valuation_model.discount_rate:.1%}")
        print(f"Terminal Growth Rate: {self.valuation_model.terminal_growth_rate:.1%}")
        print("-"*50)
        print(f"Intrinsic Value (Total Equity): {intrinsic_value_total:,.2f} {self.company.currency}")
        print(f"Intrinsic Value Per Share: {intrinsic_value_per_share:.2f} {self.company.currency}")

        if self.market_price:
            margin_of_safety = (intrinsic_value_per_share - self.market_price) / self.market_price
            print(f"Current Market Price: {self.market_price:.2f} {self.company.currency}")
            print(f"Margin of Safety: {margin_of_safety:.1%}")

        print("="*50)

    def export_to_dict(self) -> Dict[str, float]:
        """Export valuation results as a dictionary."""
        intrinsic_value_total = self.valuation_model.calculate_value()
        intrinsic_value_per_share = self.valuation_model.calculate_intrinsic_per_share(self.shares_outstanding)

        report_data = {
            "Company": self.company.name,
            "Ticker": self.company.ticker,
            "Currency": self.company.currency,
            "Intrinsic Value Total": intrinsic_value_total,
            "Intrinsic Value Per Share": intrinsic_value_per_share,
            "Discount Rate": self.valuation_model.discount_rate,
            "Payout Ratio": self.valuation_model.payout_ratio,
            "Terminal Growth Rate": self.valuation_model.terminal_growth_rate,
            "Market Price": self.market_price,
            "Margin of Safety": None
        }

        if self.market_price:
            margin_of_safety = (intrinsic_value_per_share - self.market_price) / self.market_price
            report_data["Margin of Safety"] = margin_of_safety

        return report_data
