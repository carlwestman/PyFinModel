# examples/advanced_kpi_example.py

import os
from PyFinModeler import (
    Company, AssumptionSet, ForecastRule, ForecastModel,
    DividendDiscountModel, ValuationSummaryReport,
    ChartGenerator, BorsdataCollector
)

# Step 1: Load API Key
api_key = os.environ.get("BORSDATA_API_KEY")
if not api_key:
    raise ValueError("API Key not found. Make sure BORSDATA_API_KEY is set.")

# Step 2: Initialize BorsdataCollector
collector = BorsdataCollector(api_key=api_key)

# Step 3: Fetch Company (Atlas Copco B)
company = collector.fetch_company_by_name("Atlas Copco B", report_type="year", period_type="1year")

if company is None:
    print("Company not found.")
    exit()

# Step 4: Setup Assumptions
assumptions = AssumptionSet()
assumptions.set_assumption("revenue_growth", 0.06)  # 6% Revenue Growth
assumptions.set_assumption("tax_rate", 0.25)        # 25% Tax Rate

# Step 5: Setup Forecast Model
forecast_model = ForecastModel(company=company, assumptions=assumptions, periods=5)

# Step 6: Define KPIs (using existing Börsdata fields)
forecast_model.add_kpi("Gross_Margin_Percent", "(gross_Income) / revenues")
forecast_model.add_kpi("Net_Income_Margin", "profit_To_Equity_Holders / revenues")

# Step 7: Define Forecast Rules
forecast_model.add_forecast_rule(ForecastRule(
    item_name="revenues",
    method="growth_rate",
    params={"rate": 0.06}
))

forecast_model.add_forecast_rule(ForecastRule(
    item_name="profit_To_Equity_Holders",
    method="margin_of",
    params={"base_item": "revenues", "margin": 0.20}  # Assume 20% net margin
))

# Step 8: Run Forecast
forecast_model.run_forecast()

# Step 9: Valuation using DDM
ddm_model = DividendDiscountModel(
    company=company,
    base_item_for_dividends="profit_To_Equity_Holders",
    discount_rate=0.08,
    payout_ratio=0.5,
    terminal_growth_rate=0.02,
    periods=5
)

shares_outstanding = 100
market_price = 12.00

report = ValuationSummaryReport(
    company=company,
    valuation_model=ddm_model,
    shares_outstanding=shares_outstanding,
    market_price=market_price
)
report.generate()

# Step 10: Charting
output_folder = "charts_advanced"
os.makedirs(output_folder, exist_ok=True)

chart = ChartGenerator(company)

# Plot Revenues
try:
    chart.plot_financial_item("revenues", save_path=f"{output_folder}/revenues_forecast.png")
except Exception as e:
    print(f"Warning: Cannot plot revenues: {str(e)}")

# Plot Profit to Equity Holders
try:
    chart.plot_financial_item("profit_To_Equity_Holders", save_path=f"{output_folder}/profit_to_equity_forecast.png")
except Exception as e:
    print(f"Warning: Cannot plot Profit to Equity Holders: {str(e)}")

# Plot KPIs
try:
    chart.plot_kpi(company.kpi_manager, "Gross_Margin_Percent", save_path=f"{output_folder}/gross_margin_forecast.png")
    chart.plot_kpi(company.kpi_manager, "Net_Income_Margin", save_path=f"{output_folder}/net_income_margin_forecast.png")
except Exception as e:
    print(f"Warning: Cannot plot KPI: {str(e)}")
