# PyFinModeler/core/financial_item_type.py

from enum import Enum

class FinancialItemType(Enum):
    # Balance Sheet
    ASSET = "Asset"
    LIABILITY = "Liability"
    EQUITY = "Equity"

    # Income Statement
    REVENUE = "Revenue"
    EXPENSE = "Expense"
    RESULT = "Result"  # Net income, profit after tax

    # Ratios / Metrics
    RATIO = "Ratio"

    # Cash Flows
    CASH_FLOW_OPERATING = "Operating Cash Flow Item"
    CASH_FLOW_INVESTING = "Investing Cash Flow Item"
    CASH_FLOW_FINANCING = "Financing Cash Flow Item"
    CASH_FLOW_SUMMARY = "Net Cash Flow (Summary)"

    # Dividends and distributions
    DIVIDEND = "Dividends Paid"

    # Fallback
    OTHER = "Other"
