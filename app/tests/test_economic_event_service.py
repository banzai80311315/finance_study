import pandas as pd

from services.economic_event_service import events_between, load_economic_events


def test_economic_events_are_sorted_and_have_expected_columns():
    events = load_economic_events()

    assert events["date"].is_monotonic_increasing
    assert {"date", "event_title", "category", "summary", "source_url"} <= set(
        events.columns
    )


def test_events_between_filters_to_price_period():
    events = pd.DataFrame({
        "date": pd.to_datetime(["2020-01-01", "2021-01-01"]),
        "event_title": ["対象", "対象外"],
    })

    selected = events_between(
        events, pd.Timestamp("2019-12-31"), pd.Timestamp("2020-12-31")
    )

    assert selected["event_title"].tolist() == ["対象"]
