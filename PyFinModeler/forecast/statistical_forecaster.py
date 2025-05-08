import numpy as np
from typing import Dict, Optional
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet
import pandas as pd

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
            periods: Number of future periods to forecast.
            mode: 'mean', 'random', or 'percentile'.
                - 'mean': Use the historical mean for all forecasted values.
                - 'random': Generate random values based on the historical mean and standard deviation.
                - 'percentile': Use the mean plus a multiple of the standard deviation.
            std_multiplier: Multiplier for the standard deviation (used in 'percentile' mode).
            trend: Annual trend growth rate as a fraction (e.g., 0.02 for 2% growth).
            frequency: 'year' or 'quarter'.
            random_seed: For reproducibility in 'random' mode.

        Returns:
            Dict of {future period: forecast value}.

        Example:
            forecaster = StatisticalForecaster(historical={"2020": 100, "2021": 110})
            forecast = forecaster.forecast_normal(
                periods=5,
                mode="mean",
                trend=0.02,
                frequency="year"
            )
            print(forecast)
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

    def forecast_holt_winters(
        self,
        periods: int,
        trend: Optional[str] = "add",  # "add" (additive), "mul" (multiplicative), or None
        seasonal: Optional[str] = "add",  # "add" (additive), "mul" (multiplicative), or None
        seasonal_periods: int = 4,  # Number of periods in a seasonal cycle (e.g., 4 for quarterly data)
        damped_trend: bool = False,  # Whether to dampen the trend
        frequency: str = "quarter",  # "year" or "quarter"
    ) -> Dict[str, float]:
        """
        Generate forecasts using the Holt-Winters Exponential Smoothing model.

        Args:
            periods: Number of future periods to forecast.
            trend: Type of trend component ("add", "mul", or None).
            seasonal: Type of seasonal component ("add", "mul", or None).
            seasonal_periods: Number of periods in a seasonal cycle.
            damped_trend: Whether to dampen the trend.
            frequency: "year" or "quarter".

        Returns:
            Dict of {future period: forecast value}.

        Example:
            forecaster = StatisticalForecaster(historical={"2020Q1": 100, "2020Q2": 120})
            forecast = forecaster.forecast_holt_winters(
                periods=8,
                trend="add",
                seasonal="add",
                seasonal_periods=4,
                frequency="quarter"
            )
            print(forecast)
        """
        if not self.historical:
            raise ValueError("Historical data is empty. Cannot perform forecasting.")

        # Prepare the data for the model
        historical_values = list(self.historical.values())

        # Fit the Holt-Winters model
        model = ExponentialSmoothing(
            historical_values,
            trend=trend,
            seasonal=seasonal,
            seasonal_periods=seasonal_periods,
            damped_trend=damped_trend,
        )
        fitted_model = model.fit()

        # Generate forecasts
        forecast_values = fitted_model.forecast(periods)

        # Parse the last period to generate future period keys
        last_period = self.period_keys[-1]
        forecast = {}
        if frequency == "year":
            current_year = int(last_period[:4])
            for i, value in enumerate(forecast_values, start=1):
                forecast[str(current_year + i)] = round(value, 2)
        elif frequency == "quarter":
            try:
                current_year, current_q = map(int, last_period.split("Q"))
            except ValueError:
                raise ValueError("Historical keys must be in 'YYYYQ#' format for quarterly frequency.")
            for i, value in enumerate(forecast_values, start=1):
                current_q += 1
                if current_q > 4:
                    current_q = 1
                    current_year += 1
                forecast[f"{current_year}Q{current_q}"] = round(value, 2)
        else:
            raise ValueError("Frequency must be 'year' or 'quarter'.")

        return forecast

    def forecast_sarima(
        self,
        periods: int,
        order: tuple = (1, 1, 1),  # (p, d, q) for ARIMA
        seasonal_order: tuple = (0, 0, 0, 0),  # (P, D, Q, s) for SARIMA
        trend: Optional[str] = None,  # 'n', 'c', 't', or 'ct'
        frequency: str = "year",  # 'year' or 'quarter'
    ) -> Dict[str, float]:
        """
        Generate forecasts using the SARIMA model.

        Args:
            periods: Number of future periods to forecast.
            order: ARIMA order (p, d, q).
            seasonal_order: SARIMA seasonal order (P, D, Q, s).
            trend: Trend parameter ('n', 'c', 't', or 'ct').
            frequency: 'year' or 'quarter'.

        Returns:
            Dict of {future period: forecast value}.

        Example:
            forecaster = StatisticalForecaster(historical={"2020": 100, "2021": 110})
            forecast = forecaster.forecast_sarima(
                periods=5,
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, 4),
                trend="c",
                frequency="year"
            )
            print(forecast)
        """
        if not self.historical:
            raise ValueError("Historical data is empty. Cannot perform forecasting.")

        # Prepare the data for the model
        historical_values = list(self.historical.values())

        # Fit the SARIMA model
        model = SARIMAX(
            historical_values,
            order=order,
            seasonal_order=seasonal_order,
            trend=trend,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fitted_model = model.fit(disp=False)

        # Generate forecasts
        forecast_values = fitted_model.forecast(steps=periods)

        # Parse the last period to generate future period keys
        last_period = self.period_keys[-1]
        forecast = {}
        if frequency == "year":
            current_year = int(last_period[:4])
            for i, value in enumerate(forecast_values, start=1):
                forecast[str(current_year + i)] = round(value, 2)
        elif frequency == "quarter":
            try:
                current_year, current_q = map(int, last_period.split("Q"))
            except ValueError:
                raise ValueError("Historical keys must be in 'YYYYQ#' format for quarterly frequency.")
            for i, value in enumerate(forecast_values, start=1):
                current_q += 1
                if current_q > 4:
                    current_q = 1
                    current_year += 1
                forecast[f"{current_year}Q{current_q}"] = round(value, 2)
        else:
            raise ValueError("Frequency must be 'year' or 'quarter'.")

        return forecast

    def forecast_prophet(
        self,
        periods: int,
        frequency: str = "year",  # 'year' or 'quarter'
        growth: str = "linear",  # 'linear', 'logistic', or 'flat'
        seasonality_mode: str = "additive",  # 'additive' or 'multiplicative'
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = False,
        daily_seasonality: bool = False,
        holidays: Optional[pd.DataFrame] = None,
    ) -> Dict[str, float]:
        """
        Generate forecasts using the Prophet model.

        Args:
            periods: Number of future periods to forecast.
            frequency: 'year' or 'quarter'.
            growth: Growth type ('linear', 'logistic', or 'flat').
            seasonality_mode: Seasonality mode ('additive' or 'multiplicative').
            yearly_seasonality: Whether to include yearly seasonality.
            weekly_seasonality: Whether to include weekly seasonality.
            daily_seasonality: Whether to include daily seasonality.
            holidays: Optional DataFrame with holiday information.

        Returns:
            Dict of {future period: forecast value}.

        Example:
            forecaster = StatisticalForecaster(historical={"2020": 100, "2021": 110})
            forecast = forecaster.forecast_prophet(
                periods=5,
                frequency="year",
                growth="linear",
                seasonality_mode="additive",
                yearly_seasonality=True
            )
            print(forecast)
        """
        if not self.historical:
            raise ValueError("Historical data is empty. Cannot perform forecasting.")

        # Prepare the data for Prophet
        historical_df = pd.DataFrame({
            "ds": pd.to_datetime(self.period_keys),
            "y": self.values,
        })

        # Initialize the Prophet model
        model = Prophet(
            growth=growth,
            seasonality_mode=seasonality_mode,
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
            holidays=holidays,
        )

        # Fit the model
        model.fit(historical_df)

        # Create a future dataframe
        if frequency == "year":
            freq = "Y"
        elif frequency == "quarter":
            freq = "Q"
        else:
            raise ValueError("Frequency must be 'year' or 'quarter'.")

        future = model.make_future_dataframe(periods=periods, freq=freq)

        # Generate forecasts
        forecast = model.predict(future)

        # Extract forecasted values for future periods
        forecasted_values = forecast.tail(periods)["yhat"].values

        # Parse the last period to generate future period keys
        last_period = self.period_keys[-1]
        forecast_dict = {}
        if frequency == "year":
            current_year = int(last_period[:4])
            for i, value in enumerate(forecasted_values, start=1):
                forecast_dict[str(current_year + i)] = round(value, 2)
        elif frequency == "quarter":
            try:
                current_year, current_q = map(int, last_period.split("Q"))
            except ValueError:
                raise ValueError("Historical keys must be in 'YYYYQ#' format for quarterly frequency.")
            for i, value in enumerate(forecasted_values, start=1):
                current_q += 1
                if current_q > 4:
                    current_q = 1
                    current_year += 1
                forecast_dict[f"{current_year}Q{current_q}"] = round(value, 2)
        else:
            raise ValueError("Frequency must be 'year' or 'quarter'.")

        return forecast_dict
