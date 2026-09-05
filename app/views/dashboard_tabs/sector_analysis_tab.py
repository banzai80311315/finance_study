import pandas as pd
import streamlit as st

from lib.charting import line_chart
from services.stock_service import get_price_data, load_stock_master

TAB_NAME = "同セクター分析"
ORDER = 25

SECTOR_PERIODS = {
    "1年": "1y",
    "3年": "3y",
    "5年": "5y",
}


def _normalize_prices(prices: pd.DataFrame) -> pd.DataFrame:
    normalized = prices.copy()
    for column in normalized.columns:
        first_value = normalized[column].dropna().iloc[0]
        normalized[column] = normalized[column] / first_value * 100
    return normalized


def render(context):
    ticker = context["ticker"]
    company_name = context["company_name"]
    stock_master = load_stock_master()
    selected_rows = stock_master[stock_master["ticker"] == ticker]

    if selected_rows.empty:
        st.error("選択銘柄のセクター情報を取得できませんでした。")
        return

    selected_stock = selected_rows.iloc[0]
    sector = selected_stock["sector"]
    sector_stocks = stock_master[stock_master["sector"] == sector].copy()

    st.header("同セクター分析")
    st.caption(
        f"{company_name}と同じ「{sector}」に分類された銘柄を、基準日を100として比較します。"
    )

    period_label = st.selectbox(
        "比較期間", list(SECTOR_PERIODS), index=0, key="sector_analysis_period"
    )
    period = SECTOR_PERIODS[period_label]

    price_series = {}
    failures = []
    with st.spinner("同セクターの株価データを取得しています..."):
        for row in sector_stocks.itertuples(index=False):
            try:
                price_data = get_price_data(row.ticker, period=period)
                close = price_data["Close"].dropna()
                if close.empty:
                    raise ValueError("終値データがありません")
                label = (
                    f"{row.company_name}（対象銘柄）"
                    if row.ticker == ticker
                    else row.company_name
                )
                price_series[label] = close
            except Exception:
                failures.append(row.company_name)

    if not price_series:
        st.error("同セクターの株価データを取得できませんでした。")
        return

    if failures:
        st.warning(f"取得できなかった銘柄: {', '.join(failures)}")

    stock_labels = list(price_series)
    prices = pd.concat(price_series, axis=1).sort_index()
    normalized = _normalize_prices(prices)
    normalized["同セクター平均"] = normalized[stock_labels].mean(axis=1)

    st.subheader("基準日を100とした推移")
    st.altair_chart(line_chart(normalized, "指数（基準日=100）"), width="stretch")

    st.subheader("期間リターン比較")
    latest = normalized.ffill().iloc[-1]
    returns = (latest - 100).sort_values(ascending=False)
    return_table = pd.DataFrame({
        "銘柄": returns.index,
        "期間リターン": [f"{value:+.2f}%" for value in returns.values],
    })
    st.dataframe(return_table, width="stretch", hide_index=True)

    st.caption(
        "同セクター平均は、取得できた個別株の基準日=100の指数を単純平均したものです。"
    )
