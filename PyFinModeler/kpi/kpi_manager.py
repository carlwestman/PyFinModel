# PyFinModeler/kpi/kpi_manager.py

import re

class KPIManager:
    def __init__(self, company):
        """
        Initialize KPIManager.
        
        Args:
            company: Company object to reference financial statements
        """
        self.company = company
        self.kpis = {}  # {kpi_name: formula string or constant value}

    def add_kpi(self, kpi_name: str, formula: str) -> None:
        """Add a new KPI definition."""
        self.kpis[kpi_name] = formula

    def calculate_kpi(self, kpi_name: str) -> dict:
        """Calculate KPI values across periods."""
        formula = self.kpis.get(kpi_name)
        if not formula:
            raise ValueError(f"KPI '{kpi_name}' is not defined.")

        variables = self._extract_variables(formula)

        periods = set()
        for var in variables:
            item = self._find_item(var)
            if item:
                periods.update(item.historical.keys())
                periods.update(item.forecasted.keys())

        periods = sorted(periods)

        results = {}
        for period in periods:
            local_vars = {}
            for var in variables:
                item = self._find_item(var)
                if item:
                    value = item.get_value(period)
                    local_vars[var] = value if value is not None else 0
                else:
                    # If the variable is actually a constant (e.g., 15.2), eval will catch it
                    try:
                        local_vars[var] = float(var)
                    except:
                        local_vars[var] = 0

            try:
                result = eval(formula, {}, local_vars)
                results[period] = result
            except ZeroDivisionError:
                results[period] = None  # Handle divide by zero gracefully

        return results

    def _extract_variables(self, formula: str) -> list:
        """Extract variable names from a formula string."""
        return list(set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", formula)))

    def _find_item(self, item_name: str):
        """Find a FinancialItem across company financial statements."""
        return (
            self.company.income_statement.get_item(item_name)
            or self.company.balance_sheet.get_item(item_name)
            or self.company.cash_flow_statement.get_item(item_name)
        )
