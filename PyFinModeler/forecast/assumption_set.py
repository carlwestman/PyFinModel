# PyFinModeler/forecast/assumption_set.py

from typing import Dict, Union, Optional

class AssumptionSet:
    def __init__(self):
        self.assumptions: Dict[str, Union[float, Dict[str, float]]] = {}

    def set_assumption(self, key: str, value: Union[float, Dict[str, float]]) -> None:
        """Set a forecasting assumption."""
        self.assumptions[key] = value

    def get_assumption(self, key: str) -> Optional[Union[float, Dict[str, float]]]:
        """Retrieve a forecasting assumption."""
        return self.assumptions.get(key)

    def get_growth_for_period(self, key: str, period: str) -> Optional[float]:
        """Retrieve growth rate for a specific period."""
        assumption = self.get_assumption(key)
        if isinstance(assumption, dict):
            return assumption.get(period)
        return assumption

    def to_dict(self) -> Dict:
        return self.assumptions

    def load_from_dict(self, data: Dict) -> None:
        self.assumptions = data
