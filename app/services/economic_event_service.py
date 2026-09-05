from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ECONOMIC_EVENTS_PATH = DATA_DIR / "economic_events.csv"
REQUIRED_COLUMNS = {"date", "event_title", "category", "summary", "source_url"}


@st.cache_data(ttl=3600, show_spinner=False)
def load_economic_events() -> pd.DataFrame:
    if not ECONOMIC_EVENTS_PATH.exists():
        raise FileNotFoundError(
            f"経済イベントCSVが存在しません: {ECONOMIC_EVENTS_PATH}"
        )

    events = pd.read_csv(ECONOMIC_EVENTS_PATH, parse_dates=["date"])
    if not REQUIRED_COLUMNS.issubset(events.columns):
        missing = sorted(REQUIRED_COLUMNS - set(events.columns))
        raise ValueError(f"経済イベントCSVに必須列がありません: {', '.join(missing)}")
    if events["date"].isna().any():
        raise ValueError("経済イベントCSVに有効でない日付があります。")

    return events.sort_values("date").reset_index(drop=True)


def events_between(
    events: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    start_date = pd.Timestamp(start).date()
    end_date = pd.Timestamp(end).date()
    event_dates = events["date"].dt.date
    return events.loc[(event_dates >= start_date) & (event_dates <= end_date)].copy()
