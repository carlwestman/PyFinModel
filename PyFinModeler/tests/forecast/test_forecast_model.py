import pytest
from unittest.mock import MagicMock
from PyFinModeler.forecast.forecast_model import ForecastModel
from PyFinModeler.forecast.forecast_rule import ForecastRule
from PyFinModeler.core.company import Company
from PyFinModeler.core.financial_item import FinancialItem
from PyFinModeler.core.financial_item_type import FinancialItemType
from PyFinModeler.kpi.kpi_manager import KPIManager


def test_forecast_model_initialization():
    """Test initialization of a ForecastModel."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    assumptions = MagicMock()  # Mock assumptions
    model = ForecastModel(company=company, assumptions=assumptions, periods=5, frequency="Annual")

    assert model.company == company
    assert model.assumptions == assumptions
    assert model.periods == 5
    assert model.frequency == "Annual"
    assert model.rules == []
    assert isinstance(model.kpi_manager, KPIManager)


def test_add_forecast_rule():
    """Test adding a forecast rule to the ForecastModel."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    assumptions = MagicMock()
    model = ForecastModel(company=company, assumptions=assumptions)

    rule = ForecastRule(item_name="Revenue", method="growth_rate", params={"rate": 0.1})
    model.add_forecast_rule(rule)

    assert len(model.rules) == 1
    assert model.rules[0] == rule


def test_add_kpi():
    """Test adding a KPI to the ForecastModel."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    assumptions = MagicMock()
    model = ForecastModel(company=company, assumptions=assumptions)

    model.add_kpi(kpi_name="NetProfitMargin", formula="NetProfit / Revenue * 100")
    assert "NetProfitMargin" in model.kpi_manager.kpis


def test_find_item():
    """Test finding a financial item across all financial statements."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE)
    company.income_statement.add_item(item)

    assumptions = MagicMock()
    model = ForecastModel(company=company, assumptions=assumptions)

    found_item = model._find_item("Revenue")
    assert found_item == item

    # Test finding a non-existent item
    assert model._find_item("NonExistentItem") is None


def test_run_forecast():
    """Test running a forecast with a simple growth rate rule."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE, historical={"2023": 1000.0})
    company.income_statement.add_item(item)

    assumptions = MagicMock()
    model = ForecastModel(company=company, assumptions=assumptions, periods=3, frequency="Annual")

    rule = ForecastRule(item_name="Revenue", method="growth_rate", params={"rate": 0.1})
    model.add_forecast_rule(rule)

    model.run_forecast()

    # Verify forecasted values
    assert item.forecasted["2024"] == 1100.0
    assert item.forecasted["2025"] == 1210.0
    assert item.forecasted["2026"] == 1331.0