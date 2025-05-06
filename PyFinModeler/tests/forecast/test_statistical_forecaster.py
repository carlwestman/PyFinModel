import pytest
from PyFinModeler.forecast.statistical_forecaster import StatisticalForecaster


def test_statistical_forecaster_initialization():
    """Test initialization of the StatisticalForecaster."""
    historical_data = {"2023": 1000.0, "2022": 900.0, "2021": 800.0}
    forecaster = StatisticalForecaster(historical_data)

    assert forecaster.historical == historical_data


def test_forecast_normal_default_parameters():
    """Test forecast_normal with default parameters."""
    historical_data = {"2023": 1000.0, "2022": 900.0, "2021": 800.0}
    forecaster = StatisticalForecaster(historical_data)

    forecasted = forecaster.forecast_normal(periods=3)
    assert len(forecasted) == 3
    assert all(isinstance(value, float) for value in forecasted.values())


def test_forecast_normal_with_custom_parameters():
    """Test forecast_normal with custom parameters."""
    historical_data = {"2023": 1000.0, "2022": 900.0, "2021": 800.0}
    forecaster = StatisticalForecaster(historical_data)

    forecasted = forecaster.forecast_normal(
        periods=3,
        mode="mean",
        std_multiplier=1.5,
        trend=0.05,
        frequency="year",
        random_seed=42,
    )

    assert len(forecasted) == 3
    assert all(isinstance(value, float) for value in forecasted.values())

    # Verify reproducibility with random_seed
    forecasted_again = forecaster.forecast_normal(
        periods=3,
        mode="mean",
        std_multiplier=1.5,
        trend=0.05,
        frequency="year",
        random_seed=42,
    )
    assert forecasted == forecasted_again


def test_forecast_normal_with_invalid_mode():
    """Test forecast_normal with an invalid mode."""
    historical_data = {"2023": 1000.0, "2022": 900.0, "2021": 800.0}
    forecaster = StatisticalForecaster(historical_data)

    with pytest.raises(ValueError, match="Unsupported mode"):
        forecaster.forecast_normal(periods=3, mode="invalid_mode")


def test_forecast_normal_with_invalid_frequency():
    """Test forecast_normal with an invalid frequency."""
    historical_data = {"2023": 1000.0, "2022": 900.0, "2021": 800.0}
    forecaster = StatisticalForecaster(historical_data)

    with pytest.raises(ValueError, match="frequency must be 'year' or 'quarter'"):
        forecaster.forecast_normal(periods=3, frequency="invalid_frequency")


def test_forecast_normal_with_empty_historical_data():
    """Test forecast_normal with empty historical data."""
    historical_data = {}
    forecaster = StatisticalForecaster(historical_data)

    forecasted = forecaster.forecast_normal(periods=3)
    assert len(forecasted) == 0  # No forecast should be generated