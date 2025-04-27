# examples/full_example.py

from PyFinModeler import (
    Company, FinancialItem, FinancialItemType,
    AssumptionSet, ForecastRule, ForecastModel,
    DividendDiscountModel, ValuationSummaryReport,
    ChartGenerator, KPIManager
)

import os

# Step 1: Create Company and Financial Items
company = Company(name="ExampleCo", ticker="EXC", currency="USD")

revenue = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE)
revenue.add_historical("2023", 1000)

cogs = FinancialItem(name="COGS", item_type=FinancialItemType.EXPENSE)
cogs.add_historical("2023", 600)

net_income = FinancialItem(name="Net Income", item_type=FinancialItemType.EXPENSE)
net_income.add_historical("2023", 250)

company.income_statement.add_item(revenue)
company.income_statement.add_item(cogs)
company.income_statement.add_item(net_income)

# Step 2: Setup Assumptions
assumptions = AssumptionSet()
assumptions.set_assumption("revenue_growth", 0.06)
assumptions.set_assumption("cogs_to_revenue_ratio", 0.58)
assumptions.set_assumption("tax_rate", 0.25)

# Step 3: Define Forecast Rules
def forecast_net_income(item, model):
    revenue_item = model._find_item("Revenue")
    cogs_item = model._find_item("COGS")
    tax_rate = model.assumptions.get_assumption("tax_rate")

    for period in revenue_item.forecasted.keys():
        earnings_before_tax = revenue_item.forecasted[period] - cogs_item.forecasted[period]
        net_income_value = earnings_before_tax * (1 - tax_rate)
        item.add_forecasted(period, net_income_value)

forecast_model = ForecastModel(company=company, assumptions=assumptions, periods=5)

forecast_model.add_forecast_rule(ForecastRule("Revenue", method="growth_rate", params={"rate": 0.06}))
forecast_model.add_forecast_rule(ForecastRule("COGS", method="margin_of", params={"base_item": "Revenue", "margin": 0.58}))
forecast_model.add_forecast_rule(ForecastRule("Net Income", method="custom_function", custom_function=forecast_net_income))

forecast_model.run_forecast()

# Step 4: Valuation
ddm_model = DividendDiscountModel(
    company=company,
    discount_rate=0.08,
    payout_ratio=0.5,
    terminal_growth_rate=0.02,
    periods=5
)

shares_outstanding = 100_000_000
market_price = 12.00

report = ValuationSummaryReport(
    company=company,
    valuation_model=ddm_model,
    shares_outstanding=shares_outstanding,
    market_price=market_price
)
report.generate()

# Step 5: Charting
output_folder = "charts"
os.makedirs(output_folder, exist_ok=True)

chart = ChartGenerator(company)
chart.plot_financial_item("Revenue", save_path=f"{output_folder}/revenue_forecast.png")
chart.plot_financial_item("Net Income", save_path=f"{output_folder}/net_income_forecast.png")

# Step 6: Define and plot a KPI
kpi_manager = KPIManager(company)
kpi_manager.add_kpi("Gross Margin %", "(Revenue - COGS) / Revenue")

chart.plot_kpi(kpi_manager, "Gross Margin %", save_path=f"{output_folder}/gross_margin_forecast.png")
