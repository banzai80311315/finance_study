import pandas as pd

from services.analysis_service import add_moving_average, judge_golden_cross, judge_trend


def test_custom_moving_average_windows_are_used_by_judgement():
    prices = pd.DataFrame({"Close": [1, 2, 3, 4, 5, 6]})
    result = add_moving_average(prices, short_window=2, long_window=3)

    assert judge_trend(result, short_window=2, long_window=3) == "上昇トレンド"
    assert judge_golden_cross(result, short_window=2, long_window=3) == "シグナルなし"
