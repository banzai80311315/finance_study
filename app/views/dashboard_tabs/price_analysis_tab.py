import streamlit as st

from lib.charting import bar_chart, line_chart
from lib.glossary import term_help
from services.stock_service import get_price_data
from services.economic_event_service import events_between, load_economic_events
from services.analysis_service import (
    add_moving_average,
    judge_trend,
    judge_golden_cross,
)

TAB_NAME = "株価分析"
ORDER = 20

PRICE_PERIODS = {
    "5営業日": "5d",
    "1か月": "1mo",
    "3か月": "3mo",
    "6か月": "6mo",
    "1年": "1y",
    "2年": "2y",
    "5年": "5y",
    "10年": "10y",
    "年初来": "ytd",
    "全期間": "max",
}


def render(context):
    ticker = context["ticker"]

    st.header("株価分析")

    try:
        selected_period = st.selectbox(
            "表示期間",
            list(PRICE_PERIODS),
            index=4,
            key="price_analysis_period",
        )
        period = PRICE_PERIODS[selected_period]

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

        if len(price_df) < long_window:
            st.info(
                f"選択期間のデータは{len(price_df)}件です。"
                f"長期移動平均（{long_window}日）の判定にはデータが不足しているため、"
                "終値を中心に表示します。"
            )

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
    col5.metric("株価トレンド", trend_result, help=term_help("株価トレンド"))
    col6.metric(
        "ゴールデンクロス判定",
        golden_cross_result,
        help=term_help("ゴールデンクロス"),
    )

    st.subheader("終値・移動平均チャート")
    chart_df = price_df[["Close", f"MA{short_window}", f"MA{long_window}"]].dropna(
        how="all"
    )
    try:
        economic_events = events_between(
            load_economic_events(), price_df.index.min(), price_df.index.max()
        )
    except (FileNotFoundError, ValueError):
        economic_events = None

    if economic_events is not None and not economic_events.empty:
        st.caption("オレンジの縦線は、表示期間内の登録済み経済イベントです。")
    st.altair_chart(
        line_chart(chart_df, "価格（円）", events=economic_events),
        width="stretch",
    )
    if economic_events is not None and not economic_events.empty:
        st.subheader("経済イベントを確認")
        st.caption("チャート上のオレンジ線は、下のイベント選択と対応しています。")
        event_labels = economic_events.apply(
            lambda row: f"{row['date']:%Y-%m-%d}  {row['event_title']}", axis=1
        )
        selected_event_label = st.selectbox(
            "イベントを選択",
            event_labels.tolist(),
            key="price_analysis_economic_event",
        )
        selected_event = economic_events.loc[event_labels == selected_event_label].iloc[
            0
        ]
        detail_col, source_col = st.columns([4, 1])
        detail_col.markdown(
            f"**{selected_event['category']}**  {selected_event['summary']}"
        )
        source_url = str(selected_event["source_url"])
        if source_url.startswith("https://"):
            source_col.link_button("出典を開く", source_url)

    st.subheader("出来高チャート")
    st.altair_chart(bar_chart(price_df["Volume"], "出来高"), width="stretch")
