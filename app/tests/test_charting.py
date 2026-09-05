import pandas as pd
import pytest

from lib.charting import candlestick_chart, padded_domain
from lib.charting import line_chart


def test_padded_domain_uses_minimum_and_maximum_across_all_series():
    data = pd.DataFrame({"A": [100, 120], "B": [90, 130]})

    assert padded_domain(data) == (89.0, 131.0)


def test_padded_domain_ignores_missing_values():
    data = pd.Series([float("nan"), 5.0, 15.0])

    assert padded_domain(data) == (4.0, 16.0)


def test_candlestick_chart_contains_wick_and_body_layers():
    data = pd.DataFrame(
        {
            "Open": [100.0, 105.0],
            "High": [110.0, 112.0],
            "Low": [95.0, 101.0],
            "Close": [105.0, 103.0],
        },
        index=pd.date_range("2026-01-01", periods=2),
    )

    chart_spec = candlestick_chart(data).to_dict()

    assert len(chart_spec["layer"]) == 2
    assert chart_spec["layer"][0]["mark"] == {"type": "rule"}
    assert chart_spec["layer"][1]["mark"]["type"] == "bar"


def test_candlestick_chart_requires_ohlc_columns():
    with pytest.raises(ValueError, match="Open"):
        candlestick_chart(pd.DataFrame({"Close": [100.0]}))


def test_line_chart_adds_economic_event_layer():
    prices = pd.Series(
        [100.0, 101.0],
        index=pd.date_range("2020-01-01", periods=2),
        name="Close",
    )
    events = pd.DataFrame({
        "date": pd.to_datetime(["2020-01-01"]),
        "event_title": ["イベント"],
        "category": ["金融"],
        "summary": ["概要"],
        "source_url": ["https://example.com"],
    })

    chart_spec = line_chart(prices, "価格", events=events).to_dict()

    assert len(chart_spec["layer"]) == 2
    assert chart_spec["layer"][1]["mark"]["type"] == "rule"
