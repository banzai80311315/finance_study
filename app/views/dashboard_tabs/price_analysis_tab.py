import streamlit as st

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

        price_df = get_price_data(ticker=ticker, period=period)

        price_df = add_moving_average(
            df=price_df,
            short_window=25,
            long_window=75,
        )

        trend_result = judge_trend(price_df)
        golden_cross_result = judge_golden_cross(price_df)

    except Exception as e:
        st.error("株価データの取得または分析に失敗しました。")
        st.write(e)
        return

    latest = price_df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("現在株価", f"{latest['Close']:,.0f}円")
    col2.metric("高値", f"{latest['High']:,.0f}円")
    col3.metric("安値", f"{latest['Low']:,.0f}円")
    col4.metric("出来高", f"{latest['Volume']:,.0f}")

    st.subheader("トレンド判定")

    col5, col6 = st.columns(2)
    col5.metric("株価トレンド", trend_result)
    col6.metric("ゴールデンクロス判定", golden_cross_result)

    st.subheader("終値・移動平均チャート")
    chart_df = price_df[["Close", "MA25", "MA75"]].dropna()
    st.line_chart(chart_df)

    st.subheader("出来高チャート")
    st.bar_chart(price_df["Volume"])

    st.subheader("明日の株価予測")
    st.info("ここに予測モデルの結果を追加します。")
