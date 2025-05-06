import pytest
import os
import json
from PyFinModeler.core.company import Company
from PyFinModeler.core.financial_item import FinancialItem
from PyFinModeler.core.financial_item_type import FinancialItemType


def test_company_initialization():
    """Test initialization of a Company object."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    assert company.name == "TestCo"
    assert company.ticker == "TCO"
    assert company.currency == "USD"
    assert company.income_statement.statement_name == "Income Statement"
    assert company.balance_sheet.statement_name == "Balance Sheet"
    assert company.cash_flow_statement.statement_name == "Cash Flow Statement"
    assert company.kpi_statement.statement_name == "KPI Statement"
    assert company.other_financials_statement.statement_name == "Other Financials Statement"


def test_add_financial_item_to_income_statement():
    """Test adding a financial item to the Income Statement."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE)
    company.income_statement.add_item(item)

    retrieved_item = company.income_statement.get_item("Revenue")
    assert retrieved_item == item
    assert retrieved_item.name == "Revenue"
    assert retrieved_item.item_type == FinancialItemType.REVENUE


def test_save_to_json(tmp_path):
    """Test saving a Company object to a JSON file."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE, historical={"2023": 1000.0})
    company.income_statement.add_item(item)

    file_path = tmp_path / "company.json"
    company.save_to_json(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["name"] == "TestCo"
    assert data["ticker"] == "TCO"
    assert data["currency"] == "USD"
    assert "income_statement" in data["financials"]
    assert "Revenue" in data["financials"]["income_statement"]
    assert data["financials"]["income_statement"]["Revenue"]["historical"] == {"2023": 1000.0}


def test_load_from_json(tmp_path):
    """Test loading a Company object from a JSON file."""
    file_path = tmp_path / "company.json"
    data = {
        "name": "TestCo",
        "ticker": "TCO",
        "currency": "USD",
        "financials": {
            "income_statement": {
                "Revenue": {
                    "type": "Revenue",
                    "historical": {"2023": 1000.0},
                    "forecasted": {},
                }
            },
            "balance_sheet": {},
            "cash_flow_statement": {},
            "kpi_statement": {},
            "other_financials_statement": {},
        },
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    company = Company(name="", ticker="", currency="")
    company.load_from_json(file_path)

    assert company.name == "TestCo"
    assert company.ticker == "TCO"
    assert company.currency == "USD"
    retrieved_item = company.income_statement.get_item("Revenue")
    assert retrieved_item.name == "Revenue"
    assert retrieved_item.item_type == FinancialItemType.REVENUE
    assert retrieved_item.historical == {"2023": 1000.0}


def test_to_dict():
    """Test converting a Company object to a dictionary."""
    company = Company(name="TestCo", ticker="TCO", currency="USD")
    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE, historical={"2023": 1000.0})
    company.income_statement.add_item(item)

    company_dict = company.to_dict()
    assert company_dict["name"] == "TestCo"
    assert company_dict["ticker"] == "TCO"
    assert company_dict["currency"] == "USD"
    assert "income_statement" in company_dict["financials"]
    assert "Revenue" in company_dict["financials"]["income_statement"]
    assert company_dict["financials"]["income_statement"]["Revenue"]["historical"] == {"2023": 1000.0}