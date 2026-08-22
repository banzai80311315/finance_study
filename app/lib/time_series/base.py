from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ModelMetadata:
    """Human-readable information shown in the research workbench."""

    key: str
    name: str
    description: str
    assumptions: tuple[str, ...]
    reference: str = ""


class ForecastModel(ABC):
    """Contract implemented by every forecasting method.

    A paper implementation only needs to subclass this class and register one
    instance in ``models.py``.  The UI and backtester can then use it without
    knowing its internal algorithm.
    """

    metadata: ModelMetadata
    minimum_observations: int = 2

    @abstractmethod
    def forecast(self, train: pd.Series, horizon: int) -> pd.Series:
        """Return ``horizon`` forecasts fitted only on ``train``."""

    def validate(self, train: pd.Series, horizon: int) -> pd.Series:
        clean = train.dropna().astype(float)
        if len(clean) < self.minimum_observations:
            raise ValueError(
                f"{self.metadata.name}には{self.minimum_observations}件以上の観測が必要です。"
            )
        if horizon < 1:
            raise ValueError("予測期間は1以上で指定してください。")
        return clean
