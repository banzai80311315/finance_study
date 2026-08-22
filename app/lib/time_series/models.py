from collections.abc import Iterable

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from lib.time_series.base import ForecastModel, ModelMetadata
from lib.time_series.particle_filter import LocalLevelParticleFilterModel


class NaiveModel(ForecastModel):
    metadata = ModelMetadata(
        key="naive",
        name="ナイーブ（直近値）",
        description="直近の終値が将来も続くと仮定する比較基準モデルです。",
        assumptions=("直近値が最良の予測値", "構造変化を明示的に扱わない"),
        reference="Random walk benchmark",
    )

    def forecast(self, train: pd.Series, horizon: int) -> pd.Series:
        clean = self.validate(train, horizon)
        return pd.Series(np.repeat(clean.iloc[-1], horizon), dtype=float)


class DriftModel(ForecastModel):
    metadata = ModelMetadata(
        key="drift",
        name="ドリフト",
        description="先頭から直近までの平均変化量を将来へ線形外挿します。",
        assumptions=("期間平均のトレンドが予測期間も継続",),
        reference="Random walk with drift",
    )
    minimum_observations = 3

    def forecast(self, train: pd.Series, horizon: int) -> pd.Series:
        clean = self.validate(train, horizon)
        slope = (clean.iloc[-1] - clean.iloc[0]) / (len(clean) - 1)
        steps = np.arange(1, horizon + 1)
        return pd.Series(clean.iloc[-1] + slope * steps, dtype=float)


class ArimaModel(ForecastModel):
    metadata = ModelMetadata(
        key="arima_110",
        name="ARIMA(1,1,0)",
        description="一階差分と1期の自己回帰項で短期変動を表現します。",
        assumptions=("一階差分後の弱定常性", "残差が無相関", "パラメータの安定性"),
        reference="Box–Jenkins ARIMA",
    )
    minimum_observations = 30

    def forecast(self, train: pd.Series, horizon: int) -> pd.Series:
        clean = self.validate(train, horizon)
        fitted = ARIMA(clean.to_numpy(), order=(1, 1, 0)).fit()
        return pd.Series(fitted.forecast(steps=horizon), dtype=float)


_MODELS: dict[str, ForecastModel] = {}


def register_model(model: ForecastModel) -> None:
    """Register a model and reject accidental duplicate identifiers."""
    key = model.metadata.key
    if key in _MODELS:
        raise ValueError(f"モデルキーが重複しています: {key}")
    _MODELS[key] = model


def register_models(models: Iterable[ForecastModel]) -> None:
    for model in models:
        register_model(model)


def list_models() -> tuple[ForecastModel, ...]:
    return tuple(_MODELS.values())


def get_model(key: str) -> ForecastModel:
    try:
        return _MODELS[key]
    except KeyError as exc:
        raise ValueError(f"未登録のモデルです: {key}") from exc


register_models(
    (NaiveModel(), DriftModel(), ArimaModel(), LocalLevelParticleFilterModel())
)
