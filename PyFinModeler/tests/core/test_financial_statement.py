import pytest
from PyFinModeler.core.financial_statement import (
    FinancialStatement,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    KPIStatement,
    OtherFinancialsStatement,
)
from PyFinModeler.core.financial_item import FinancialItem
from PyFinModeler.core.financial_item_type import FinancialItemType


def test_financial_statement_initialization():
    """Test initialization of the FinancialStatement base class."""
    class TestStatement(FinancialStatement):
        def validate(self) -> bool:
            return True

    statement = TestStatement("Test Statement")
    assert statement.statement_name == "Test Statement"
    assert statement.items == {}


def test_financial_statement_add_and_get_item():
    """Test adding and retrieving financial items in a FinancialStatement."""
    class TestStatement(FinancialStatement):
        def validate(self) -> bool:
            return True

    statement = TestStatement("Test Statement")
    item = FinancialItem(name="Revenue", item_type=FinancialItemType.REVENUE)
    statement.add_item(item)

    retrieved_item = statement.get_item("Revenue")
    assert retrieved_item == item
    assert retrieved_item.name == "Revenue"
    assert retrieved_item.item_type == FinancialItemType.REVENUE


def test_financial_statement_validate_abstract_method():
    """Test that the validate method is abstract in FinancialStatement."""
    with pytest.raises(TypeError):
        FinancialStatement("Abstract Statement")


def test_income_statement_initialization():
    """Test initialization of the IncomeStatement class."""
    statement = IncomeStatement()
    assert statement.statement_name == "Income Statement"
    assert statement.items == {}


def test_income_statement_validate():
    """Test the validate method of the IncomeStatement class."""
    statement = IncomeStatement()
    assert statement.validate() is True


def test_balance_sheet_initialization():
    """Test initialization of the BalanceSheet class."""
    statement = BalanceSheet()
    assert statement.statement_name == "Balance Sheet"
    assert statement.items == {}


def test_balance_sheet_validate():
    """Test the validate method of the BalanceSheet class."""
    statement = BalanceSheet()
    assert statement.validate() is True


def test_cash_flow_statement_initialization():
    """Test initialization of the CashFlowStatement class."""
    statement = CashFlowStatement()
    assert statement.statement_name == "Cash Flow Statement"
    assert statement.items == {}


def test_cash_flow_statement_validate():
    """Test the validate method of the CashFlowStatement class."""
    statement = CashFlowStatement()
    assert statement.validate() is True


def test_kpi_statement_initialization():
    """Test initialization of the KPIStatement class."""
    statement = KPIStatement()
    assert statement.statement_name == "KPI Statement"
    assert statement.items == {}


def test_kpi_statement_validate():
    """Test the validate method of the KPIStatement class."""
    statement = KPIStatement()
    assert statement.validate() is True


def test_other_financials_statement_initialization():
    """Test initialization of the OtherFinancialsStatement class."""
    statement = OtherFinancialsStatement()
    assert statement.statement_name == "Other Financials Statement"
    assert statement.items == {}


def test_other_financials_statement_validate():
    """Test the validate method of the OtherFinancialsStatement class."""
    statement = OtherFinancialsStatement()
    assert statement.validate() is True