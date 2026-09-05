import streamlit as st

from lib.charting import candlestick_chart
from lib.glossary import term_help
from services.stock_service import get_price_data, get_stock_info

TAB_NAME = "基本情報"
ORDER = 10

CANDLESTICK_OPTIONS = {
    "日足（1年）": ("1y", "1d"),
    "1時間足（直近60日）": ("60d", "1h"),
    "15分足（直近30日）": ("30d", "15m"),
    "5分足（直近5日）": ("5d", "5m"),
    "1分足（直近5日）": ("5d", "1m"),
}


def render(context):
    ticker = context["ticker"]
    company_name = context["company_name"]

    st.header("基本情報")

    try:
        stock_info = get_stock_info(ticker)

    except Exception:
        st.error("基本情報の取得に失敗しました。しばらく待って再度お試しください。")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("銘柄名", company_name)
    col2.metric("証券コード", ticker)
    col3.metric("業種", stock_info.get("industry", "-"))

    col4, col5, col6 = st.columns(3)
    col4.metric("セクター", stock_info.get("sector", "-"))
    col5.metric(
        "時価総額",
        stock_info.get("market_cap_text", "-"),
        help=term_help("時価総額"),
    )
    col6.metric("通貨", stock_info.get("currency", "-"))

    st.subheader("ローソク足チャート")
    selected_candlestick = st.selectbox(
        "足種と表示期間",
        list(CANDLESTICK_OPTIONS),
        key="basic_info_candlestick_option",
    )
    period, interval = CANDLESTICK_OPTIONS[selected_candlestick]

    try:
        price_df = get_price_data(
            ticker=ticker,
            period=period,
            interval=interval,
        )
        st.altair_chart(
            candlestick_chart(price_df[["Open", "High", "Low", "Close"]]),
            width="stretch",
        )
    except Exception:
        st.error(
            "ローソク足チャートを表示できませんでした。しばらく待って再度お試しください。"
        )
