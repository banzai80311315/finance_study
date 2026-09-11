import altair as alt
import pandas as pd
import streamlit as st

from lib.charting import line_chart
from lib.glossary import term_help
from lib.time_series.diagnostics import calculate_acf, calculate_diagnostics
from services.stock_service import get_price_data

TAB_NAME = "自己相関"
ORDER = 40


def _transform(close: pd.Series, method: str) -> pd.Series:
    if method == "対数リターン":
        import numpy as np

        return np.log(close).diff().dropna().rename("Log return")
    if method == "単純リターン":
        return close.pct_change().dropna().rename("Return")
    return close.rename("Close")


def render(context):
    st.header("自己相関分析")
    st.caption("価格系列を変換し、自己相関と、その解釈に関わる定常性を確認します。")

    period = st.selectbox("データ期間", ["1y", "3y", "5y"], index=1, key="lab_period")
    transform_name = st.selectbox("診断対象", ["終値", "単純リターン", "対数リターン"])
    max_lag = st.slider("ACFの最大ラグ", min_value=1, max_value=60, value=20, key="lab_acf_lags")

    try:
        with st.spinner("価格データを取得し、時系列を診断しています..."):
            price_df = get_price_data(context["ticker"], period=period)
            close = price_df["Close"].dropna()
            diagnostic_series = _transform(close, transform_name)
            diagnostics = calculate_diagnostics(diagnostic_series)
            acf_values = calculate_acf(diagnostic_series, max_lag=max_lag)
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

    st.subheader("ラグ別の自己相関（ACF）")
    acf_frame = acf_values.reset_index()
    base = alt.Chart(acf_frame).encode(
        x=alt.X("Lag:Q", title="Lag（観測間隔）", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("ACF:Q", title="ACF", scale=alt.Scale(domain=[-1, 1], nice=False)),
        tooltip=[alt.Tooltip("Lag:Q", format="d"), alt.Tooltip("ACF:Q", format=".4f")],
    )
    stems = base.mark_rule().encode(y2=alt.datum(0))
    points = base.mark_point(filled=True, size=45)
    zero = alt.Chart(pd.DataFrame({"zero": [0]})).mark_rule(color="gray").encode(y="zero:Q")
    st.altair_chart((zero + stems + points).properties(height=320), width="stretch")
    st.caption(
        f"{transform_name}の標本ACFです。ラグ0は自分自身との相関で1です。"
        "日次データのラグ1は、欠損除去後の1観測前（通常は前の取引日）を表します。"
        "正は同方向、負は逆方向の関係を表し、0に近いほど線形の関係が弱いことを示します。"
        "終値の高いACFだけで、リターンの予測可能性を判断することはできません。"
    )
    if acf_values.index[-1] < max_lag:
        st.caption(f"観測数に合わせ、最大ラグを{acf_values.index[-1]}に制限しています。")

    st.subheader("診断対象の推移")
    st.altair_chart(line_chart(diagnostic_series, "値"), width="stretch")

    with st.expander("再現性メモ"):
        st.code(
            f"ticker={context['ticker']}\nperiod={period}\ntransform={transform_name}"
            f"\nacf_max_lag={acf_values.index[-1]}\nacf_adjusted=False"
        )
