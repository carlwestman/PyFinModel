# PyFinModeler/kpi/kpi_manager.py

import re
from typing import Optional


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
        """
        Add a new Key Performance Indicator (KPI) definition to the KPIManager.
        
        This method allows users to define a KPI by providing a name and a formula. 
        The formula can reference financial items (e.g., "Revenue", "Expenses") 
        or constants, and it will be used to calculate the KPI values across 
        different periods.

        Args:
            kpi_name (str): The name of the KPI to be added. This should be a unique 
                            identifier for the KPI.
            formula (str): The formula used to calculate the KPI. The formula can 
                           include variable names corresponding to financial items 
                           and mathematical operations (e.g., "Revenue - Expenses").

        Raises:
            ValueError: If the `kpi_name` is empty or already exists in the KPIManager.

        Example:
            >>> kpi_manager.add_kpi("NetProfit", "Revenue - Expenses")
            >>> kpi_manager.add_kpi("ProfitMargin", "(NetProfit / Revenue) * 100")
        """
        if kpi_name in self.kpis:
            raise ValueError(f"KPI '{kpi_name}' already exists.")
        self.kpis[kpi_name] = formula

    def add_percentage_change_kpi(self, kpi_name: str, item_name: str, lookback: int) -> None:
        """
        Add a KPI that calculates the percentage change of a financial item over a specified lookback period.

        Args:
            kpi_name (str): The name of the KPI to be added.
            item_name (str): The name of the financial item to calculate the percentage change for.
            lookback (int): The number of periods to look back for the comparison.

        Raises:
            ValueError: If the financial item is not found or if the KPI name already exists.

        Example:
            >>> kpi_manager.add_percentage_change_kpi("YoY Gross Revenue Change", "Gross Revenue", 4)
        """
        if kpi_name in self.kpis:
            raise ValueError(f"KPI '{kpi_name}' already exists.")
        
        item = self._find_item(item_name)
        if not item:
            raise ValueError(f"Financial item '{item_name}' not found.")

        def percentage_change_formula(period: str) -> Optional[float]:
            """
            Calculate the percentage change for the given period and lookback.
            """
            if "Q" in period:  # Quarterly period
                year, quarter = map(int, period.split("Q"))
                lookback_quarter = quarter - lookback
                lookback_year = year + (lookback_quarter - 1) // 4
                lookback_quarter = (lookback_quarter - 1) % 4 + 1
                lookback_period = f"{lookback_year}Q{lookback_quarter}"
            else:  # Annual period
                lookback_period = str(int(period) - lookback)

            current_value = item.get_value(period)
            previous_value = item.get_value(lookback_period)

            if current_value is None or previous_value is None or previous_value == 0:
                return None

            return ((current_value - previous_value) / previous_value) * 100

        # Store the dynamically created formula in the KPI dictionary
        self.kpis[kpi_name] = percentage_change_formula

    def calculate_kpi(self, kpi_name: str) -> dict:
        """
        Calculate the values of a Key Performance Indicator (KPI) across all periods.

        This method evaluates the formula or function associated with the specified KPI name 
        for each period, using the historical and forecasted values of the financial 
        items referenced in the formula. The result is a dictionary mapping each 
        period to the calculated KPI value.

        Args:
            kpi_name (str): The name of the KPI to calculate. This must match a KPI 
                            previously defined using the `add_kpi` method.

        Returns:
            dict: A dictionary where the keys are periods (e.g., "2025", "2025Q1") 
                  and the values are the calculated KPI values for those periods.

        Raises:
            ValueError: If the specified `kpi_name` is not defined in the KPIManager.

        Notes:
            - If a variable in the formula is not found in the financial statements, 
              it is treated as a constant or assigned a default value of 0.
            - Division by zero is handled gracefully by assigning `None` to the result 
              for that period.

        Example:
            >>> kpi_manager.add_kpi("NetProfit", "Revenue - Expenses")
            >>> kpi_manager.calculate_kpi("NetProfit")
            {'2025': 50000, '2026': 55000, '2027': 60000}
        """
        formula_or_function = self.kpis.get(kpi_name)
        if not formula_or_function:
            raise ValueError(f"KPI '{kpi_name}' is not defined.")

        # If the KPI is a callable function, evaluate it for each period
        if callable(formula_or_function):
            # Gather all periods from all financial items
            periods = set()
            for statement in [self.company.income_statement, self.company.balance_sheet, self.company.cash_flow_statement]:
                for item in statement.items.values():
                    periods.update(item.historical.keys())
                    periods.update(item.forecasted.keys())

            periods = sorted(periods)

            # Evaluate the function for each period
            results = {}
            for period in periods:
                try:
                    result = formula_or_function(period)
                    if result is not None:  # Exclude periods with None values
                        results[period] = round(result, 3)  # Round to 3 decimal places
                except Exception as e:
                    results[period] = None  # Handle errors gracefully
            return results

        # If the KPI is a formula string, evaluate it as before
        variables = self._extract_variables(formula_or_function)

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
                result = eval(formula_or_function, {}, local_vars)
                if result is not None:  # Exclude periods with None values
                    results[period] = round(result, 3)  # Round to 3 decimal places
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
            or self.company.kpi_statement.get_item(item_name)  # Added KPI Statement
            or self.company.other_financials_statement.get_item(item_name)  # Added Other Financials Statement
        )
