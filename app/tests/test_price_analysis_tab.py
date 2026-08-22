from views.dashboard_tabs.price_analysis_tab import PRICE_PERIODS


def test_price_periods_include_short_and_long_variations():
    assert PRICE_PERIODS["5営業日"] == "5d"
    assert PRICE_PERIODS["1か月"] == "1mo"
    assert PRICE_PERIODS["年初来"] == "ytd"
    assert PRICE_PERIODS["全期間"] == "max"


def test_price_periods_only_use_yfinance_supported_values():
    supported = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}

    assert set(PRICE_PERIODS.values()) <= supported
