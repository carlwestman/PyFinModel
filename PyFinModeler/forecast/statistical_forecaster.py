import numpy as np
from typing import Dict, Optional

class StatisticalForecaster:
    def __init__(self, historical: Dict[str, float]):
        """
        Initialize the StatisticalForecaster with historical data.

        Args:
            historical: Dictionary of {period: value}, e.g., {"2020": 100.0, "2021Q1": 110.0}
        """
        self.historical = historical
        self.values = list(historical.values())
        self.mean = np.mean(self.values)
        self.std = np.std(self.values)
        self.period_keys = sorted(historical.keys())

    def forecast_normal(
        self,
        periods: int,
        mode: str = "mean",
        std_multiplier: float = 1.0,
        trend: float = 0.0,
        frequency: str = "year",  # 'year' or 'quarter'
        random_seed: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Generate forecasts using a normal distribution-based model.

        Args:
            periods: Number of future periods to forecast
            mode: 'mean', 'random', or 'percentile'
            std_multiplier: Applied in 'percentile' mode
            trend: Annual trend growth rate (as fraction)
            frequency: 'year' or 'quarter'
            random_seed: For reproducible random mode

        Returns:
            Dict of {future period: forecast value}
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        if not self.period_keys:
            return {}  # Handle empty historical data gracefully

        forecast = {}

        # Parse last period
        last_period = self.period_keys[-1]
        if frequency == "year":
            current_year = int(last_period[:4])
        elif frequency == "quarter":
            try:
                current_year, current_q = map(int, last_period.split("Q"))
            except:
                raise ValueError("Historical keys must be in 'YYYYQ#' format for quarterly frequency.")
        else:
            raise ValueError("frequency must be 'year' or 'quarter'")

        for i in range(1, periods + 1):
            # Generate value
            if mode == "mean":
                val = self.mean
            elif mode == "random":
                val = np.random.normal(self.mean, self.std)
            elif mode == "percentile":
                val = self.mean + std_multiplier * self.std
            else:
                raise ValueError(f"Unsupported mode: {mode}")

            val *= (1 + trend) ** i  # Apply compound trend

            # Determine period label
            if frequency == "year":
                current_year += 1
                period_key = str(current_year)
            elif frequency == "quarter":
                current_q += 1
                if current_q > 4:
                    current_q = 1
                    current_year += 1
                period_key = f"{current_year}Q{current_q}"

            forecast[period_key] = round(float(val), 2)

        return forecast
