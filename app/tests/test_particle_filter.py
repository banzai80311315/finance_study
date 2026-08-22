import pandas as pd
import pytest

from lib.time_series.particle_filter import LocalLevelParticleFilterModel


def _sample_prices() -> pd.Series:
    return pd.Series([100 + index * 0.2 for index in range(80)], dtype=float)


def test_particle_filter_returns_positive_requested_horizon():
    model = LocalLevelParticleFilterModel(particle_count=200, random_seed=42)
    forecast = model.forecast(_sample_prices(), horizon=5)

    assert len(forecast) == 5
    assert forecast.notna().all()
    assert (forecast > 0).all()


def test_particle_filter_is_reproducible_with_same_seed():
    first = LocalLevelParticleFilterModel(
        particle_count=200, random_seed=7
    ).forecast(_sample_prices(), horizon=3)
    second = LocalLevelParticleFilterModel(
        particle_count=200, random_seed=7
    ).forecast(_sample_prices(), horizon=3)

    pd.testing.assert_series_equal(first, second)


def test_particle_filter_rejects_non_positive_prices():
    prices = _sample_prices()
    prices.iloc[-1] = 0

    with pytest.raises(ValueError, match="0より大きい"):
        LocalLevelParticleFilterModel(particle_count=200).forecast(prices, horizon=1)
