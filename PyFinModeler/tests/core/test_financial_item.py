import pytest
from PyFinModeler.core.financial_item import FinancialItem
from PyFinModeler.core.financial_item_type import FinancialItemType


def test_financial_item_initialization():
    """Test initialization of a FinancialItem."""
    item = FinancialItem(
        name="Revenue",
        item_type=FinancialItemType.REVENUE,
        historical={"2023": 1000.0},
        forecasted={"2024": 1200.0},
    )
    assert item.name == "Revenue"
    assert item.item_type == FinancialItemType.REVENUE
    assert item.historical == {"2023": 1000.0}
    assert item.forecasted == {"2024": 1200.0}


def test_add_historical_data():
    """Test adding historical data to a FinancialItem."""
    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE)
    item.add_historical("2023", 1000.0)
    assert item.historical == {"2023": 1000.0}

    # Test overwriting existing historical data
    item.add_historical("2023", 1100.0)
    assert item.historical == {"2023": 1100.0}


def test_add_forecasted_data():
    """Test adding forecasted data to a FinancialItem."""
    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE)
    item.add_forecasted("2024", 1200.0)
    assert item.forecasted == {"2024": 1200.0}

    # Test overwriting existing forecasted data
    item.add_forecasted("2024", 1300.0)
    assert item.forecasted == {"2024": 1300.0}


def test_get_value():
    """Test retrieving values from a FinancialItem."""
    item = FinancialItem(
        name="Revenue",
        item_type=FinancialItemType.REVENUE,
        historical={"2023": 1000.0},
        forecasted={"2024": 1200.0},
    )

    # Test retrieving historical value
    assert item.get_value("2023") == 1000.0

    # Test retrieving forecasted value
    assert item.get_value("2024") == 1200.0

    # Test retrieving a non-existent period
    assert item.get_value("2025") is None


def test_empty_historical_and_forecasted_data():
    """Test a FinancialItem with no historical or forecasted data."""
    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE)
    assert item.historical == {}
    assert item.forecasted == {}

    # Test retrieving a value from an empty item
    assert item.get_value("2023") is None