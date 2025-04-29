# examples/advanced_kpi_example.py

import os
from PyFinModeler import (
    Company, AssumptionSet, ForecastRule, ForecastModel,
    DividendDiscountModel, ValuationSummaryReport, ScenarioModel,
    ChartGenerator, BorsdataCollector, BorsdataKPICollector,
    FinancialItem, FinancialItemType
)

# Step 1: Load API Key
api_key = os.environ.get("BORSDATA_API_KEY")
if not api_key:
    raise ValueError("API Key not found. Please set BORSDATA_API_KEY.")

# Step 2: Initialize collectors
collector = BorsdataCollector(api_key=api_key)
kpi_collector = BorsdataKPICollector(api_key=api_key)

# Step 3: Fetch Company (Atlas Copco B)
company, instrument_id, company_info = collector.fetch_company_by_name("Atlas Copco B", report_type="year")

if company is None:
    print("Company not found.")
    exit()

# Step 4: Fetch real KPIs from Nordic endpoint
instrument_id = 1605  # Atlas Copco B

# Fetch Net Income Margin (Net Margin %)
try:
    net_income_margin_values = kpi_collector.fetch_kpis(instrument_id, kpi_id=30, report_type="year", price_type="mean")
    net_income_margin = list(net_income_margin_values.values())[0]
except Exception as e:
    print(f"Warning: Could not fetch Net Income Margin. Error: {str(e)}")
    net_income_margin = 0.20  # fallback

# Fetch Payout Ratio %
try:
    payout_ratio_values = kpi_collector.fetch_kpis(instrument_id, kpi_id=20, report_type="year", price_type="mean")
    payout_ratio = list(payout_ratio_values.values())[0] / 100
except Exception as e:
    print(f"Warning: Could not fetch Payout Ratio. Error: {str(e)}")
    payout_ratio = 0.5

# Fetch Number of Shares
try:
    shares_values = kpi_collector.fetch_kpis(instrument_id, kpi_id=61, report_type="year", price_type="mean")
    shares_outstanding = list(shares_values.values())[0]
except Exception as e:
    print(f"Warning: Could not fetch Number of Shares. Error: {str(e)}")
    shares_outstanding = 100_000_000

# Step 5: Setup Assumptions (Base Case)
base_assumptions = AssumptionSet()
base_assumptions.set_assumption("revenue_growth", 0.06)
base_assumptions.set_assumption("tax_rate", 0.25)

# Step 6: Setup Forecast Model
forecast_model = ForecastModel(company=company, assumptions=base_assumptions, periods=5)

# Step 6️⃣: Define KPIs (using financials)
forecast_model.add_kpi("Gross_Margin_Percent", "(gross_Income) / revenues")
forecast_model.add_kpi("Net_Income_Margin", "profit_To_Equity_Holders / revenues")

# Step 7: Add Dividend FinancialItem
dividends = FinancialItem(name="Dividends", item_type=FinancialItemType.DIVIDEND)
company.cash_flow_statement.add_item(dividends)

# Step 8: Define Forecast Rules
forecast_model.add_forecast_rule(ForecastRule(
    item_name="revenues",
    method="growth_rate",
    params={"rate": base_assumptions.get_assumption("revenue_growth")}
))

forecast_model.add_forecast_rule(ForecastRule(
    item_name="profit_To_Equity_Holders",
    method="margin_of",
    params={"base_item": "revenues", "margin": net_income_margin}
))

def forecast_dividends(item, model):
    profit_item = model._find_item("profit_To_Equity_Holders")
    for period, profit in profit_item.forecasted.items():
        dividend = profit * payout_ratio
        item.add_forecasted(period, dividend)

forecast_model.add_forecast_rule(ForecastRule(
    item_name="Dividends",
    method="custom_function",
    custom_function=forecast_dividends
))

# Step 9: Run Forecast
forecast_model.run_forecast()

# Step 10: Valuation using DDM
ddm_model = DividendDiscountModel(
    company=company,
    base_item_for_dividends="profit_To_Equity_Holders",
    discount_rate=0.08,
    payout_ratio=payout_ratio,
    terminal_growth_rate=0.02,
    periods=5
)

market_price = 12.00

report = ValuationSummaryReport(
    company=company,
    valuation_model=ddm_model,
    shares_outstanding=shares_outstanding,
    market_price=market_price
)
report.generate()

# Step 11: Scenario Modeling
print("\nRunning Scenario Analysis...\n")

scenario_model_base = ScenarioModel(
    company=company,
    shares_outstanding=shares_outstanding,
    market_price=market_price,
    periods=5,
    payout_ratio=payout_ratio,
    base_item_for_dividends="profit_To_Equity_Holders",
    terminal_growth_rate=0.02,
    discount_rate=0.08
)

# Bull Scenario
bull_assumptions = AssumptionSet()
bull_assumptions.set_assumption("revenue_growth", 0.08)
bull_result = scenario_model_base.run_scenario(bull_assumptions, label="Bull Case")
print(bull_result)

# Bear Scenario
bear_assumptions = AssumptionSet()
bear_assumptions.set_assumption("revenue_growth", 0.03)
bear_result = scenario_model_base.run_scenario(bear_assumptions, label="Bear Case")
print(bear_result)

# Step 12: Charting
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

# Plot Dividends
try:
    chart.plot_financial_item("Dividends", save_path=f"{output_folder}/dividends_forecast.png")
except Exception as e:
    print(f"Warning: Cannot plot Dividends: {str(e)}")

# Plot KPIs
try:
    chart.plot_kpi(company.kpi_manager, "Gross_Margin_Percent", save_path=f"{output_folder}/gross_margin_forecast.png")
    chart.plot_kpi(company.kpi_manager, "Net_Income_Margin", save_path=f"{output_folder}/net_income_margin_forecast.png")
except Exception as e:
    print(f"Warning: Cannot plot KPI: {str(e)}")
