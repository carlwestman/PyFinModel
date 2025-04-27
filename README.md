
# 📄 **Final README.md for PyFinModeler**

```markdown
# PyFinModeler

**Professional Financial Modeling and Valuation Framework in Python**

---

## 🚀 Overview

**PyFinModeler** is a complete, modular, and extensible system designed for:

- **Building company financial models** (Income Statement, Balance Sheet, Cash Flow)
- **Forecasting** future performance using dynamic rules
- **Creating and managing KPIs** (Key Performance Indicators)
- **Valuing companies** using Dividend Discount Model (DDM)
- **Running scenario analyses** (Bull/Base/Bear)
- **Visualizing financial data and KPIs** in professional charts
- **Generating investment reports**

Designed for **investment analysts**, **portfolio managers**, **strategic finance teams**, and **quantitative modelers**.

---

## 🏗️ Architecture Overview

| Module | Purpose |
|:-------|:--------|
| `core/` | Defines company structure, financial items, financial statements |
| `forecast/` | Forecast engine (assumptions, forecast rules, forecast model) |
| `valuation/` | Dividend Discount Model valuation + summary reporting |
| `scenario/` | Scenario stress testing and sensitivity analysis |
| `kpi/` | Define, manage, calculate dynamic KPIs |
| `visualization/` | Plot financial data and KPIs |
| `examples/` | Full working modeling examples |

---

## 📦 Core Modules in Detail

---

### 1. `core/` — Company and Financial Items

| Class | Purpose |
|:------|:--------|
| `Company` | Holds Income Statement, Balance Sheet, Cash Flow |
| `FinancialItem` | Represents a line item (e.g., Revenue, Cash, Debt) |
| `FinancialItemType` | Enum for Assets, Liabilities, Revenues, Expenses, Cash Flows |
| `IncomeStatement`, `BalanceSheet`, `CashFlowStatement` | Structured containers for financial items |

#### Example:

```python
from PyFinModeler import Company, FinancialItem, FinancialItemType

company = Company(name="ExampleCo", ticker="EXC", currency="USD")
revenue = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE)
revenue.add_historical("2023", 1000)
company.income_statement.add_item(revenue)
```

---

### 2. `forecast/` — Dynamic Forecasting Engine

| Class | Purpose |
|:------|:--------|
| `AssumptionSet` | Stores forecast assumptions (growth rates, margins, tax rates) |
| `ForecastRule` | Defines how to forecast each item (growth, margin, link to item, custom function, or KPI-driven) |
| `ForecastModel` | Applies rules and assumptions to build forward-looking financial statements |

#### Example:

```python
from PyFinModeler import ForecastModel, ForecastRule, AssumptionSet

assumptions = AssumptionSet()
assumptions.set_assumption("revenue_growth", 0.05)

forecast_model = ForecastModel(company, assumptions, periods=5)
forecast_model.add_forecast_rule(
    ForecastRule(item_name="Revenue", method="growth_rate", params={"rate": 0.05})
)
forecast_model.run_forecast()
```

---

### 3. `kpi/` — KPI Management and Calculation

| Class | Purpose |
|:------|:--------|
| `KPIManager` | Define KPIs dynamically using formulas like `(Revenue - COGS) / Revenue` |
|  | Calculate KPI values over time |
|  | Use KPIs for forecasting (e.g., maintaining Gross Margin %) |

#### Example:

```python
from PyFinModeler import KPIManager

kpi_manager = KPIManager(company)
kpi_manager.add_kpi("Gross Margin %", "(Revenue - COGS) / Revenue")
gross_margin_results = kpi_manager.calculate_kpi("Gross Margin %")
```

---

### 4. `valuation/` — Dividend Discount Model (DDM) and Reporting

| Class | Purpose |
|:------|:--------|
| `DividendDiscountModel` | Valuation engine based on forecasted dividends |
| `ValuationSummaryReport` | Prints and exports clean investment summaries |

#### Example:

```python
from PyFinModeler import DividendDiscountModel, ValuationSummaryReport

ddm = DividendDiscountModel(company, discount_rate=0.08, payout_ratio=0.5)
report = ValuationSummaryReport(company, valuation_model=ddm, shares_outstanding=100_000_000, market_price=12.00)
report.generate()
```

---

### 5. `scenario/` — Scenario Analysis

| Class | Purpose |
|:------|:--------|
| `ScenarioModel` | Run alternative assumptions (Bull/Base/Bear cases) |
|  | Forecast + Value company under new assumptions |
|  | Calculate margin of safety dynamically |

#### Example:

```python
from PyFinModeler import ScenarioModel, AssumptionSet

scenario_model = ScenarioModel(company, shares_outstanding=100_000_000, market_price=12.00)

bull_case = AssumptionSet()
bull_case.set_assumption("revenue_growth", 0.08)

bull_result = scenario_model.run_scenario(bull_case, label="Bull Case")
print(bull_result)
```

---

### 6. `visualization/` — Charting Financial Items and KPIs

| Class | Purpose |
|:------|:--------|
| `ChartGenerator` | Plot historical + forecasted data |
|  | Plot custom KPIs |

#### Example:

```python
from PyFinModeler import ChartGenerator

chart = ChartGenerator(company)
chart.plot_financial_item("Revenue", save_path="charts/revenue_forecast.png")
chart.plot_kpi(kpi_manager, "Gross Margin %", save_path="charts/gross_margin_forecast.png")
```

---

## 🔥 What You Can Build With PyFinModeler

- Full forecasted Income Statement, Balance Sheet, and Cash Flows
- KPI-driven strategic forecasting (e.g., maintaining Gross Margin %)
- Dividend Discount Valuations (DDM)
- Scenario Analysis for downside protection
- Beautiful professional charts for investment decks
- Dynamic investment reports for your fund or portfolio

---

## 📈 Example Workflows

| Action | Modules Used |
|:-------|:-------------|
| Forecast a company's Revenue, COGS, Net Income | core/, forecast/ |
| Maintain Gross Margin % at 60% | forecast/ + kpi/ |
| Value company using DDM | valuation/ |
| Plot Revenue vs Net Income vs Dividends | visualization/ |
| Run Bull/Base/Bear scenarios | scenario/ |
| Generate full investment reports | valuation/, visualization/ |

---

## 🛠️ Installation

```bash
pip install .
```

or for live development:

```bash
pip install -e .
```

---

## 📂 Example Files

- `examples/full_example.py` — Basic modeling flow
- `examples/advanced_kpi_example.py` — KPI-driven advanced modeling

---

## 📜 License

MIT License — free to use, modify, and distribute.

---
