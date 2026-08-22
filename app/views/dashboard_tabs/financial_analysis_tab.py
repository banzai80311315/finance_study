import streamlit as st

from lib.glossary import term_help
from services.financial_service import get_financial_summary
from services.analysis_service import judge_valuation

TAB_NAME = "財務分析"
ORDER = 30


def render(context):
    ticker = context["ticker"]

    st.header("財務分析")

    try:
        financial_summary = get_financial_summary(ticker)

        valuation_comment = judge_valuation(
            per=financial_summary.get("per"),
            pbr=financial_summary.get("pbr"),
        )

    except Exception:
        st.error("財務データを取得できませんでした。しばらく待って再度お試しください。")
        return

    st.subheader("財務指標")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PER", financial_summary.get("per_text", "-"), help=term_help("PER"))
    col2.metric("PBR", financial_summary.get("pbr_text", "-"), help=term_help("PBR"))
    col3.metric("ROE", financial_summary.get("roe_text", "-"), help=term_help("ROE"))
    col4.metric(
        "時価総額",
        financial_summary.get("market_cap_text", "-"),
        help=term_help("時価総額"),
    )

    st.subheader("収益性")

    col5, col6, col7 = st.columns(3)
    col5.metric("売上高", financial_summary.get("revenue_text", "-"))
    col6.metric("営業利益", financial_summary.get("operating_income_text", "-"))
    col7.metric("当期純利益", financial_summary.get("net_income_text", "-"))

    st.subheader("安全性")

    col8, col9 = st.columns(2)
    col8.metric("総資産", financial_summary.get("total_assets_text", "-"))
    col9.metric("自己資本", financial_summary.get("equity_text", "-"))

    st.subheader("簡易判定")
    st.info(valuation_comment)
