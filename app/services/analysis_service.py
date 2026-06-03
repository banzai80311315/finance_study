import pandas as pd


def add_moving_average(
    df: pd.DataFrame, short_window: int = 25, long_window: int = 75
) -> pd.DataFrame:
    result = df.copy()

    result[f"MA{short_window}"] = result["Close"].rolling(window=short_window).mean()
    result[f"MA{long_window}"] = result["Close"].rolling(window=long_window).mean()

    return result


def judge_trend(df: pd.DataFrame) -> str:
    clean_df = df.dropna()

    if clean_df.empty:
        return "判定不可"

    latest = clean_df.iloc[-1]

    close = latest["Close"]
    ma25 = latest["MA25"]
    ma75 = latest["MA75"]

    if close > ma25 > ma75:
        return "上昇トレンド"
    elif close < ma25 < ma75:
        return "下降トレンド"
    else:
        return "横ばい・判定保留"


def judge_golden_cross(df: pd.DataFrame) -> str:
    clean_df = df.dropna()

    if len(clean_df) < 2:
        return "判定不可"

    previous = clean_df.iloc[-2]
    latest = clean_df.iloc[-1]

    prev_short = previous["MA25"]
    prev_long = previous["MA75"]

    latest_short = latest["MA25"]
    latest_long = latest["MA75"]

    if prev_short <= prev_long and latest_short > latest_long:
        return "ゴールデンクロス"
    elif prev_short >= prev_long and latest_short < latest_long:
        return "デッドクロス"
    else:
        return "シグナルなし"


def judge_valuation(per, pbr) -> str:
    if per is None and pbr is None:
        return "PER・PBRを取得できないため、割安性を判定できません。"

    comments = []

    if pbr is not None:
        if pbr < 1:
            comments.append(
                "PBRが1倍未満のため、純資産ベースでは割安と見られる可能性があります。"
            )
        elif pbr < 1.5:
            comments.append(
                "PBRは比較的低めで、資産価値に対して過度な割高感は大きくありません。"
            )
        else:
            comments.append(
                "PBRはやや高めで、資産価値に対して市場評価が上乗せされています。"
            )

    if per is not None:
        if per < 10:
            comments.append(
                "PERは低めで、利益水準に対して割安と見られる可能性があります。"
            )
        elif per < 20:
            comments.append("PERは標準的な水準です。")
        else:
            comments.append(
                "PERは高めで、将来成長への期待が織り込まれている可能性があります。"
            )

    return "\n".join(comments)
