import streamlit as st

from services.stock_service import get_stock_info, get_price_data
from services.analysis_service import (
    add_moving_average,
    judge_trend,
    judge_golden_cross,
    judge_valuation,
)
from services.financial_service import get_financial_summary


def show_dashboard_page():
    ticker = st.session_state.selected_ticker
    company_name = st.session_state.selected_company_name

    if ticker is None:
        st.session_state.page = "top"
        st.rerun()

    st.title(f"{company_name} ダッシュボード")
    st.write(f"証券コード：{ticker}")

    if st.button("トップ画面へ戻る"):
        st.session_state.page = "top"
        st.rerun()

    st.divider()

    try:
        stock_info = get_stock_info(ticker)

        period = st.selectbox("表示期間", ["6mo", "1y", "3y", "5y", "10y"], index=1)

        price_df = get_price_data(ticker=ticker, period=period)

        price_df = add_moving_average(df=price_df, short_window=25, long_window=75)

        trend_result = judge_trend(price_df)
        golden_cross_result = judge_golden_cross(price_df)

        financial_summary = get_financial_summary(ticker)
        valuation_comment = judge_valuation(
            per=financial_summary.get("per"), pbr=financial_summary.get("pbr")
        )

    except Exception as e:
        st.error("データ取得または分析処理に失敗しました。")
        st.write(e)
        return

    tab1, tab2, tab3 = st.tabs(["基本情報", "株価分析", "財務分析"])

    with tab1:
        st.header("基本情報")

        col1, col2, col3 = st.columns(3)
        col1.metric("銘柄名", company_name)
        col2.metric("証券コード", ticker)
        col3.metric("業種", stock_info.get("industry", "-"))

        col4, col5, col6 = st.columns(3)
        col4.metric("セクター", stock_info.get("sector", "-"))
        col5.metric("時価総額", stock_info.get("market_cap_text", "-"))
        col6.metric("通貨", stock_info.get("currency", "-"))

    with tab2:
        st.header("株価分析")

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

    with tab3:
        st.header("財務分析")

        st.subheader("財務指標")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("PER", financial_summary.get("per_text", "-"))
        col2.metric("PBR", financial_summary.get("pbr_text", "-"))
        col3.metric("ROE", financial_summary.get("roe_text", "-"))
        col4.metric("時価総額", financial_summary.get("market_cap_text", "-"))

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
