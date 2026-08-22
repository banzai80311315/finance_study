import pandas as pd
import streamlit as st

from lib.charting import line_chart
from lib.glossary import term_help
from lib.time_series.backtesting import rolling_origin_backtest
from lib.time_series.diagnostics import calculate_diagnostics
from lib.time_series.models import get_model, list_models
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
    st.header("時系列研究ワークベンチ")
    st.caption(
        "モデルの仮定を確認し、未来情報を使わないローリング検証で比較します。"
    )

    models = list_models()
    model_by_name = {model.metadata.name: model for model in models}

    setup_col, model_col = st.columns(2)
    period = setup_col.selectbox(
        "データ期間", ["1y", "3y", "5y", "10y"], index=2, key="lab_period"
    )
    selected_name = model_col.selectbox("予測モデル", list(model_by_name))
    model = get_model(model_by_name[selected_name].metadata.key)

    transform_col, test_col, horizon_col = st.columns(3)
    transform_name = transform_col.selectbox(
        "診断対象", ["終値", "単純リターン", "対数リターン"]
    )
    test_size = int(test_col.number_input("検証営業日数", 5, 120, 30))
    horizon = int(horizon_col.number_input("将来予測日数", 1, 30, 5))

    with st.expander("モデルの前提と位置づけ", expanded=True):
        st.write(model.metadata.description)
        st.markdown("\n".join(f"- {item}" for item in model.metadata.assumptions))
        if model.metadata.reference:
            st.caption(f"系譜・参考: {model.metadata.reference}")

    try:
        with st.spinner("価格データを取得し、時系列モデルを検証しています..."):
            price_df = get_price_data(context["ticker"], period=period)
            close = price_df["Close"].dropna()
            diagnostic_series = _transform(close, transform_name)
            diagnostics = calculate_diagnostics(diagnostic_series)
            backtest = rolling_origin_backtest(close, model, test_size=test_size)
            future = model.forecast(close, horizon=horizon)
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

    st.subheader("アウト・オブ・サンプル検証")
    metric_columns = st.columns(4)
    for column, key in zip(metric_columns, ("MAE", "RMSE", "MAPE", "Bias")):
        suffix = "%" if key == "MAPE" else "円"
        column.metric(
            key,
            f"{backtest.metrics[key]:,.2f}{suffix}",
            help=term_help(key),
        )
    st.altair_chart(
        line_chart(backtest.predictions[["Actual", "Predicted"]], "価格（円）"),
        width="stretch",
    )

    st.subheader(f"将来{horizon}営業日の条件付き予測")
    future_index = pd.RangeIndex(1, horizon + 1, name="Step")
    future.index = future_index
    st.altair_chart(
        line_chart(future.rename("Forecast"), "予測価格（円）"), width="stretch"
    )
    st.dataframe(future.rename("予測値（円）").to_frame(), width="stretch")

    with st.expander("再現性メモ"):
        st.code(
            f"ticker={context['ticker']}\nperiod={period}\n"
            f"model={model.metadata.key}\ntest_size={test_size}\nhorizon={horizon}"
        )
