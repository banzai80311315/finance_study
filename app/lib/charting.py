import altair as alt
import numpy as np
import pandas as pd


AXIS_PADDING = 1.0


def padded_domain(data: pd.Series | pd.DataFrame) -> tuple[float, float]:
    """Return a shared Y domain of plotted minimum - 1 and maximum + 1."""
    values = data.to_numpy(dtype=float).reshape(-1)
    finite_values = values[np.isfinite(values)]
    if finite_values.size == 0:
        raise ValueError("グラフに表示できる有限の数値がありません。")
    return (
        float(finite_values.min()) - AXIS_PADDING,
        float(finite_values.max()) + AXIS_PADDING,
    )


def line_chart(
    data: pd.Series | pd.DataFrame,
    y_title: str,
    height: int = 420,
    events: pd.DataFrame | None = None,
) -> alt.Chart:
    frame = data.to_frame() if isinstance(data, pd.Series) else data.copy()
    frame.columns = [str(column) for column in frame.columns]
    index_type = "T" if isinstance(frame.index, pd.DatetimeIndex) else "Q"
    chart_data = (
        frame
        .rename_axis("Index")
        .reset_index()
        .melt(id_vars="Index", var_name="系列", value_name="値")
    )
    y_min, y_max = padded_domain(frame)

    chart = (
        alt
        .Chart(chart_data)
        .mark_line()
        .encode(
            x=alt.X(f"Index:{index_type}", title="日付" if index_type == "T" else None),
            y=alt.Y(
                "値:Q",
                title=y_title,
                scale=alt.Scale(domain=[y_min, y_max], zero=False, nice=False),
            ),
            color=alt.Color("系列:N", title=None),
            tooltip=[
                alt.Tooltip(
                    f"Index:{index_type}", title="日付" if index_type == "T" else "位置"
                ),
                alt.Tooltip("系列:N"),
                alt.Tooltip("値:Q", format=",.4f"),
            ],
        )
    )
    if events is not None and not events.empty:
        event_layer = (
            alt
            .Chart(events)
            .mark_rule(color="#f59e0b", strokeDash=[4, 4], strokeWidth=3)
            .encode(x=alt.X("date:T"))
        )
        chart = chart + event_layer

    return chart.properties(height=height).interactive()


def candlestick_chart(
    data: pd.DataFrame,
    height: int = 420,
) -> alt.Chart:
    required_columns = {"Open", "High", "Low", "Close"}
    if not required_columns.issubset(data.columns):
        missing = ", ".join(sorted(required_columns - set(data.columns)))
        raise ValueError(f"ローソク足に必要な列がありません: {missing}")

    frame = data[["Open", "High", "Low", "Close"]].copy()
    frame = frame.rename_axis("Index").reset_index()
    frame["Direction"] = np.where(frame["Close"] >= frame["Open"], "上昇", "下降")
    y_min, y_max = padded_domain(frame[["Low", "High"]])
    index_type = "T" if isinstance(data.index, pd.DatetimeIndex) else "Q"
    x = alt.X(
        f"Index:{index_type}",
        title="日付" if index_type == "T" else None,
    )
    y_scale = alt.Scale(domain=[y_min, y_max], zero=False, nice=False)
    tooltip = [
        alt.Tooltip(
            f"Index:{index_type}", title="日付" if index_type == "T" else "位置"
        ),
        alt.Tooltip("Open:Q", title="始値", format=",.2f"),
        alt.Tooltip("High:Q", title="高値", format=",.2f"),
        alt.Tooltip("Low:Q", title="安値", format=",.2f"),
        alt.Tooltip("Close:Q", title="終値", format=",.2f"),
    ]

    wick = (
        alt
        .Chart(frame)
        .mark_rule()
        .encode(
            x=x,
            y=alt.Y("Low:Q", title="価格（円）", scale=y_scale),
            y2="High:Q",
            color=alt.Color(
                "Direction:N",
                scale=alt.Scale(domain=["上昇", "下降"], range=["#2f855a", "#c53030"]),
                legend=None,
            ),
            tooltip=tooltip,
        )
    )
    body = (
        alt
        .Chart(frame)
        .mark_bar(size=7)
        .encode(
            x=x,
            y=alt.Y("Open:Q", scale=y_scale),
            y2="Close:Q",
            color=alt.Color(
                "Direction:N",
                scale=alt.Scale(domain=["上昇", "下降"], range=["#2f855a", "#c53030"]),
                legend=None,
            ),
            tooltip=tooltip,
        )
    )

    return (wick + body).properties(height=height).interactive()


def bar_chart(
    data: pd.Series | pd.DataFrame,
    y_title: str,
    height: int = 320,
) -> alt.Chart:
    frame = data.to_frame() if isinstance(data, pd.Series) else data.copy()
    frame.columns = [str(column) for column in frame.columns]
    index_type = "T" if isinstance(frame.index, pd.DatetimeIndex) else "Q"
    chart_data = (
        frame
        .rename_axis("Index")
        .reset_index()
        .melt(id_vars="Index", var_name="系列", value_name="値")
    )
    y_min, y_max = padded_domain(frame)

    return (
        alt
        .Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X(f"Index:{index_type}", title="日付" if index_type == "T" else None),
            y=alt.Y(
                "値:Q",
                title=y_title,
                scale=alt.Scale(domain=[y_min, y_max], zero=False, nice=False),
            ),
            color=alt.Color("系列:N", title=None),
            tooltip=[
                alt.Tooltip(
                    f"Index:{index_type}", title="日付" if index_type == "T" else "位置"
                ),
                alt.Tooltip("系列:N"),
                alt.Tooltip("値:Q", format=",.4f"),
            ],
        )
        .properties(height=height)
        .interactive()
    )
