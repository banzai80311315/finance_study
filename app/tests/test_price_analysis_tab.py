from views.dashboard_tabs.price_analysis_tab import PRICE_PERIODS
from views.dashboard_tabs.basic_info_tab import CANDLESTICK_OPTIONS


def test_price_periods_include_short_and_long_variations():
    assert PRICE_PERIODS["5営業日"] == "5d"
    assert PRICE_PERIODS["1か月"] == "1mo"
    assert PRICE_PERIODS["年初来"] == "ytd"
    assert PRICE_PERIODS["全期間"] == "max"


def test_price_periods_only_use_yfinance_supported_values():
    supported = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}

    assert set(PRICE_PERIODS.values()) <= supported


def test_candlestick_options_pair_intraday_intervals_with_short_periods():
    assert CANDLESTICK_OPTIONS["日足（1年）"] == ("1y", "1d")
    assert CANDLESTICK_OPTIONS["1分足（直近5日）"] == ("5d", "1m")
