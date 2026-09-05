import pandas as pd
import pytest

from views.dashboard_tabs.sector_analysis_tab import (
    SECTOR_PERIODS,
    _normalize_prices,
)


def test_sector_periods_are_supported_yfinance_periods():
    assert set(SECTOR_PERIODS.values()) == {"1y", "3y", "5y"}


def test_normalize_prices_starts_each_series_at_100():
    prices = pd.DataFrame(
        {
            "対象": [100.0, 110.0],
            "比較": [200.0, 180.0],
        },
        index=pd.date_range("2026-01-01", periods=2),
    )

    normalized = _normalize_prices(prices)

    assert normalized.iloc[0].tolist() == [100.0, 100.0]
    assert normalized.iloc[-1].tolist() == pytest.approx([110.0, 90.0])
