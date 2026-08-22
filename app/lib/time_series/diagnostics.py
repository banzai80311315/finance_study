from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller


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
    lag1 = clean.autocorr(lag=1)

    return DiagnosticsResult(
        observations=len(clean),
        adf_statistic=float(adf[0]),
        adf_p_value=float(adf[1]),
        ljung_box_p_value=float(ljung_box["lb_pvalue"].iloc[-1]),
        lag1_autocorrelation=float(lag1) if not np.isnan(lag1) else float("nan"),
    )
