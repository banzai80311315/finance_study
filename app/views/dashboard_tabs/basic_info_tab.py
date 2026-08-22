import streamlit as st

from lib.glossary import term_help
from services.stock_service import get_stock_info

TAB_NAME = "基本情報"
ORDER = 10


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
