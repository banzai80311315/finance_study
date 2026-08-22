import altair as alt
import streamlit as st

from lib.glossary import term_help
from services.stock_service import get_price_data
from services.analysis_service import (
    add_moving_average,
    judge_trend,
    judge_golden_cross,
)

TAB_NAME = "株価分析"
ORDER = 20


def render(context):
    ticker = context["ticker"]

    st.header("株価分析")

    try:
        period = st.selectbox(
            "表示期間",
            ["6mo", "1y", "3y", "5y", "10y"],
            index=1,
            key="price_analysis_period",
        )

        col_short, col_long = st.columns(2)
        short_window = col_short.number_input("短期移動平均", 2, 100, 25)
        long_window = col_long.number_input("長期移動平均", 3, 250, 75)
        if short_window >= long_window:
            st.warning("短期移動平均は長期移動平均より短くしてください。")
            return

        price_df = get_price_data(ticker=ticker, period=period)

        price_df = add_moving_average(
            df=price_df,
            short_window=short_window,
            long_window=long_window,
        )

        trend_result = judge_trend(price_df, short_window, long_window)
        golden_cross_result = judge_golden_cross(price_df, short_window, long_window)

    except Exception:
        st.error("株価データを取得できませんでした。しばらく待って再度お試しください。")
        return

    latest = price_df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("現在株価", f"{latest['Close']:,.0f}円")
    col2.metric("高値", f"{latest['High']:,.0f}円")
    col3.metric("安値", f"{latest['Low']:,.0f}円")
    col4.metric("出来高", f"{latest['Volume']:,.0f}")

    st.subheader("トレンド判定")

    col5, col6 = st.columns(2)
    col5.metric(
        "株価トレンド", trend_result, help=term_help("株価トレンド")
    )
    col6.metric(
        "ゴールデンクロス判定",
        golden_cross_result,
        help=term_help("ゴールデンクロス"),
    )

    st.subheader("終値・移動平均チャート")
    chart_df = price_df[
        ["Close", f"MA{short_window}", f"MA{long_window}"]
    ].dropna()
    chart_data = (
        chart_df.rename_axis("Date")
        .reset_index()
        .melt(id_vars="Date", var_name="系列", value_name="価格")
    )
    y_min = float(price_df["Low"].min()) - 10
    y_max = float(price_df["High"].max()) + 10
    price_chart = (
        alt.Chart(chart_data)
        .mark_line()
        .encode(
            x=alt.X("Date:T", title="日付"),
            y=alt.Y(
                "価格:Q",
                title="価格（円）",
                scale=alt.Scale(domain=[y_min, y_max], zero=False),
            ),
            color=alt.Color("系列:N", title=None),
            tooltip=[
                alt.Tooltip("Date:T", title="日付"),
                alt.Tooltip("系列:N"),
                alt.Tooltip("価格:Q", format=",.2f"),
            ],
        )
        .properties(height=420)
        .interactive()
    )
    st.altair_chart(price_chart, width="stretch")

    st.subheader("出来高チャート")
    st.bar_chart(price_df["Volume"])
