# PyFinModeler/forecast/forecast_rule.py

from typing import Callable, Dict, Union, Optional

class ForecastRule:
    def __init__(
        self,
        item_name: str,
        method: str,
        params: Optional[Dict[str, Union[float, str, Dict[str, float]]]] = None,
        custom_function: Optional[Callable[[object, object], None]] = None,
        uses_kpi: bool = False  # NEW
    ):
        """
        item_name: FinancialItem or KPI name
        method: 'growth_rate', 'margin_of', 'fixed', 'link_to_item', 'custom_function'
        params: forecasting parameters
        custom_function: optional custom logic
        uses_kpi: True if the item is a KPI instead of a direct FinancialItem
        """
        self.item_name = item_name
        self.method = method
        self.params = params or {}
        self.custom_function = custom_function
        self.uses_kpi = uses_kpi
