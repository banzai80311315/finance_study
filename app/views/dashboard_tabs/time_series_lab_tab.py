import pandas as pd
import streamlit as st

from lib.charting import line_chart
from lib.glossary import term_help
from lib.time_series.diagnostics import calculate_diagnostics
from services.stock_service import get_price_data

TAB_NAME = "時系列ラボ"
ORDER = 40


def _transform(close: pd.Series, method: str) -> pd.Series:
    if method == "対数リターン":
        import numpy as np

        return np.log(close).diff().dropna().rename("Log return")
    if method == "単純リターン":
        return close.pct_change().dropna().rename("Return")
    return close.rename("Close")


def render(context):
    st.header("時系列の基礎診断")
    st.caption("価格系列を変換し、定常性と自己相関を確認します。")

    period = st.selectbox("データ期間", ["1y", "3y", "5y"], index=1, key="lab_period")
    transform_name = st.selectbox("診断対象", ["終値", "単純リターン", "対数リターン"])

    try:
        with st.spinner("価格データを取得し、時系列を診断しています..."):
            price_df = get_price_data(context["ticker"], period=period)
            close = price_df["Close"].dropna()
            diagnostic_series = _transform(close, transform_name)
            diagnostics = calculate_diagnostics(diagnostic_series)
    except Exception as exc:
        st.error(f"分析を完了できませんでした: {exc}")
        return

    st.subheader("時系列診断")
    diagnostic_columns = st.columns(4)
    diagnostic_columns[0].metric("観測数", f"{diagnostics.observations:,}")
    diagnostic_columns[1].metric(
        "ADF p値",
        f"{diagnostics.adf_p_value:.4f}",
        help=term_help("ADF p値"),
    )
    diagnostic_columns[2].metric(
        "Ljung–Box p値",
        f"{diagnostics.ljung_box_p_value:.4f}",
        help=term_help("Ljung–Box p値"),
    )
    diagnostic_columns[3].metric(
        "ラグ1自己相関",
        f"{diagnostics.lag1_autocorrelation:.3f}",
        help=term_help("ラグ1自己相関"),
    )
    st.caption(
        "ADFは小さいp値ほど単位根を棄却する根拠が強く、Ljung–Boxは小さいp値ほど自己相関の存在を示唆します。"
    )

    st.subheader("診断対象の推移")
    st.altair_chart(line_chart(diagnostic_series, "値"), width="stretch")

    with st.expander("再現性メモ"):
        st.code(
            f"ticker={context['ticker']}\nperiod={period}\ntransform={transform_name}"
        )
