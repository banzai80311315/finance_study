from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf, adfuller


def calculate_acf(series: pd.Series, max_lag: int = 20) -> pd.Series:
    """Sample ACF using the full-series mean and lag-zero variance (adjusted=False)."""
    clean = series.dropna().astype(float)
    if len(clean) < 2 or not np.isfinite(clean.to_numpy()).all():
        raise ValueError("ACFには有限の値からなる2件以上の観測が必要です。")
    if clean.nunique() < 2:
        raise ValueError("値が一定の系列ではACFを計算できません。")
    if not isinstance(max_lag, int) or max_lag < 1:
        raise ValueError("最大ラグは1以上の整数にしてください。")
    effective_lag = min(max_lag, len(clean) - 1)
    values = acf(clean.to_numpy(), nlags=effective_lag, adjusted=False, fft=False)
    return pd.Series(values, index=pd.RangeIndex(len(values), name="Lag"), name="ACF")


@dataclass(frozen=True)
class DiagnosticsResult:
    observations: int
    adf_statistic: float
    adf_p_value: float
    ljung_box_p_value: float
    lag1_autocorrelation: float


def calculate_diagnostics(series: pd.Series, lags: int = 10) -> DiagnosticsResult:
    clean = series.dropna().astype(float)
    if len(clean) < max(20, lags + 2):
        raise ValueError("時系列診断には20件以上の観測が必要です。")

    effective_lags = min(lags, len(clean) // 5)
    adf = adfuller(clean.to_numpy(), autolag="AIC")
    ljung_box = acorr_ljungbox(clean, lags=[effective_lags], return_df=True)
    lag1 = calculate_acf(clean, max_lag=1).iloc[1]

    return DiagnosticsResult(
        observations=len(clean),
        adf_statistic=float(adf[0]),
        adf_p_value=float(adf[1]),
        ljung_box_p_value=float(ljung_box["lb_pvalue"].iloc[-1]),
        lag1_autocorrelation=float(lag1) if not np.isnan(lag1) else float("nan"),
    )
