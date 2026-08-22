import pandas as pd
import pytest

from lib.time_series.backtesting import regression_metrics, rolling_origin_backtest
from lib.time_series.models import DriftModel, NaiveModel


def test_regression_metrics_for_known_values():
    metrics = regression_metrics(pd.Series([10, 20]), pd.Series([12, 18]))
    assert metrics["MAE"] == pytest.approx(2.0)
    assert metrics["RMSE"] == pytest.approx(2.0)
    assert metrics["Bias"] == pytest.approx(0.0)


def test_rolling_origin_keeps_test_dates_and_avoids_future_data():
    index = pd.date_range("2025-01-01", periods=10)
    series = pd.Series(range(1, 11), index=index, dtype=float)
    result = rolling_origin_backtest(series, NaiveModel(), test_size=3)

    assert result.predictions.index.tolist() == index[-3:].tolist()
    assert result.predictions["Predicted"].tolist() == [7.0, 8.0, 9.0]


def test_drift_model_extrapolates_linear_series():
    forecast = DriftModel().forecast(pd.Series([1.0, 2.0, 3.0]), horizon=2)
    assert forecast.tolist() == [4.0, 5.0]
