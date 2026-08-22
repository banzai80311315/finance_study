from dataclasses import dataclass

import numpy as np
import pandas as pd

from lib.time_series.base import ForecastModel


@dataclass(frozen=True)
class BacktestResult:
    predictions: pd.DataFrame
    metrics: dict[str, float]


def regression_metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    actual_values = actual.to_numpy(dtype=float)
    predicted_values = predicted.to_numpy(dtype=float)
    errors = actual_values - predicted_values
    nonzero = actual_values != 0

    metrics = {
        "MAE": float(np.mean(np.abs(errors))),
        "RMSE": float(np.sqrt(np.mean(errors**2))),
        "Bias": float(np.mean(predicted_values - actual_values)),
    }
    metrics["MAPE"] = (
        float(np.mean(np.abs(errors[nonzero] / actual_values[nonzero])) * 100)
        if nonzero.any()
        else float("nan")
    )
    return metrics


def rolling_origin_backtest(
    series: pd.Series,
    model: ForecastModel,
    test_size: int = 30,
) -> BacktestResult:
    """One-step expanding-window validation without future-data leakage."""
    clean = series.dropna().astype(float).sort_index()
    if test_size < 1:
        raise ValueError("検証期間は1以上で指定してください。")
    if len(clean) < model.minimum_observations + test_size:
        raise ValueError(
            f"学習期間{model.minimum_observations}件と検証期間{test_size}件を確保できません。"
        )

    split = len(clean) - test_size
    rows = []
    for position in range(split, len(clean)):
        train = clean.iloc[:position]
        predicted = float(model.forecast(train, horizon=1).iloc[0])
        rows.append(
            {
                "Date": clean.index[position],
                "Actual": float(clean.iloc[position]),
                "Predicted": predicted,
                "Error": float(clean.iloc[position] - predicted),
            }
        )

    predictions = pd.DataFrame(rows).set_index("Date")
    metrics = regression_metrics(predictions["Actual"], predictions["Predicted"])
    return BacktestResult(predictions=predictions, metrics=metrics)
