import numpy as np
import pandas as pd
import streamlit as st

from lib.charting import bar_chart, line_chart
from lib.glossary import term_help
from services.stock_service import get_price_data

TAB_NAME = "リスク・リターン"
ORDER = 25


def _risk_metrics(close: pd.Series) -> dict[str, float]:
    returns = close.pct_change().dropna()
    annual_return = (1 + returns.mean()) ** 252 - 1
    annual_volatility = returns.std(ddof=1) * np.sqrt(252)
    wealth = (1 + returns).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    var95 = returns.quantile(0.05)
    return {
        "年率リターン": annual_return,
        "年率ボラティリティ": annual_volatility,
        "最大ドローダウン": drawdown.min(),
        "日次VaR (95%)": var95,
    }


def render(context):
    st.header("リスク・リターン")
    st.caption("過去の実績に基づく指標であり、将来の成果を保証するものではありません。")
    try:
        price_df = get_price_data(context["ticker"], period="5y")
        returns = price_df["Close"].pct_change().dropna()
        metrics = _risk_metrics(price_df["Close"])
    except Exception as exc:
        st.error(f"リスク指標を計算できませんでした: {exc}")
        return

    columns = st.columns(4)
    for column, (label, value) in zip(columns, metrics.items()):
        column.metric(label, f"{value:.2%}", help=term_help(label))

    st.subheader("累積リターン")
    cumulative_return = ((1 + returns).cumprod() - 1).rename("累積リターン")
    st.altair_chart(line_chart(cumulative_return, "累積リターン"), width="stretch")

    st.subheader("日次リターン分布")
    bins = pd.cut(returns, bins=30).value_counts(sort=False)
    distribution = pd.DataFrame(
        {"Return": [interval.mid for interval in bins.index], "Count": bins.values}
    ).set_index("Return")
    st.altair_chart(bar_chart(distribution["Count"], "観測数"), width="stretch")
