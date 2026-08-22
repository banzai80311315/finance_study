import altair as alt
import numpy as np
import pandas as pd


AXIS_PADDING = 10.0


def padded_domain(data: pd.Series | pd.DataFrame) -> tuple[float, float]:
    """Return a shared Y domain of plotted minimum - 10 and maximum + 10."""
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
) -> alt.Chart:
    frame = data.to_frame() if isinstance(data, pd.Series) else data.copy()
    frame.columns = [str(column) for column in frame.columns]
    index_type = "T" if isinstance(frame.index, pd.DatetimeIndex) else "Q"
    chart_data = (
        frame.rename_axis("Index")
        .reset_index()
        .melt(id_vars="Index", var_name="系列", value_name="値")
    )
    y_min, y_max = padded_domain(frame)

    return (
        alt.Chart(chart_data)
        .mark_line()
        .encode(
            x=alt.X(f"Index:{index_type}", title="日付" if index_type == "T" else None),
            y=alt.Y(
                "値:Q",
                title=y_title,
                scale=alt.Scale(domain=[y_min, y_max], zero=False),
            ),
            color=alt.Color("系列:N", title=None),
            tooltip=[
                alt.Tooltip(f"Index:{index_type}", title="日付" if index_type == "T" else "位置"),
                alt.Tooltip("系列:N"),
                alt.Tooltip("値:Q", format=",.4f"),
            ],
        )
        .properties(height=height)
        .interactive()
    )


def bar_chart(
    data: pd.Series | pd.DataFrame,
    y_title: str,
    height: int = 320,
) -> alt.Chart:
    frame = data.to_frame() if isinstance(data, pd.Series) else data.copy()
    frame.columns = [str(column) for column in frame.columns]
    index_type = "T" if isinstance(frame.index, pd.DatetimeIndex) else "Q"
    chart_data = (
        frame.rename_axis("Index")
        .reset_index()
        .melt(id_vars="Index", var_name="系列", value_name="値")
    )
    y_min, y_max = padded_domain(frame)

    return (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X(f"Index:{index_type}", title="日付" if index_type == "T" else None),
            y=alt.Y(
                "値:Q",
                title=y_title,
                scale=alt.Scale(domain=[y_min, y_max], zero=False),
            ),
            color=alt.Color("系列:N", title=None),
            tooltip=[
                alt.Tooltip(f"Index:{index_type}", title="日付" if index_type == "T" else "位置"),
                alt.Tooltip("系列:N"),
                alt.Tooltip("値:Q", format=",.4f"),
            ],
        )
        .properties(height=height)
        .interactive()
    )
