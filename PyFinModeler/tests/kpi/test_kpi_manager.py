import pytest
from PyFinModeler.kpi.kpi_manager import KPIManager
from PyFinModeler.core.company import Company
from PyFinModeler.core.financial_item import FinancialItem
from PyFinModeler.core.financial_item_type import FinancialItemType


def test_kpi_manager_initialization():
    """Test initialization of a KPIManager."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    kpi_manager = KPIManager(company)

    assert kpi_manager.company == company
    assert kpi_manager.kpis == {}


def test_add_kpi():
    """Test adding a KPI with a formula."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    kpi_manager = KPIManager(company)

    kpi_manager.add_kpi("NetProfitMargin", "NetProfit / Revenue * 100")
    assert "NetProfitMargin" in kpi_manager.kpis
    assert kpi_manager.kpis["NetProfitMargin"] == "NetProfit / Revenue * 100"


def test_add_percentage_change_kpi():
    """Test adding a percentage change KPI."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    kpi_manager = KPIManager(company)

    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE, historical={"2023": 1000.0, "2022": 900.0})
    company.income_statement.add_item(item)

    kpi_manager.add_percentage_change_kpi("YoY Revenue Growth", "Revenue", 1)
    assert "YoY Revenue Growth" in kpi_manager.kpis
    assert callable(kpi_manager.kpis["YoY Revenue Growth"])


def test_calculate_kpi_formula():
    """Test calculating a KPI based on a formula."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    kpi_manager = KPIManager(company)

    item_revenue = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE, historical={"2023": 1000.0})
    item_net_profit = FinancialItem(name="NetProfit", item_type=FinancialItemType.RESULT, historical={"2023": 200.0})
    company.income_statement.add_item(item_revenue)
    company.income_statement.add_item(item_net_profit)

    kpi_manager.add_kpi("NetProfitMargin", "NetProfit / Revenue * 100")
    results = kpi_manager.calculate_kpi("NetProfitMargin")

    assert results == {"2023": 20.0}


def test_calculate_percentage_change_kpi():
    """Test calculating a percentage change KPI."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    kpi_manager = KPIManager(company)

    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE, historical={"2023": 1000.0, "2022": 900.0})
    company.income_statement.add_item(item)

    kpi_manager.add_percentage_change_kpi("YoY Revenue Growth", "Revenue", 1)
    results = kpi_manager.calculate_kpi("YoY Revenue Growth")

    assert results == {"2023": 11.111}  # Rounded to 2 decimal places


def test_add_duplicate_kpi():
    """Test adding a KPI with a duplicate name."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    kpi_manager = KPIManager(company)

    kpi_manager.add_kpi("NetProfitMargin", "NetProfit / Revenue * 100")
    with pytest.raises(ValueError, match="KPI 'NetProfitMargin' already exists."):
        kpi_manager.add_kpi("NetProfitMargin", "NetProfit / Revenue * 100")


def test_calculate_nonexistent_kpi():
    """Test calculating a KPI that does not exist."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    kpi_manager = KPIManager(company)

    with pytest.raises(ValueError, match="KPI 'NonExistentKPI' is not defined."):
        kpi_manager.calculate_kpi("NonExistentKPI")