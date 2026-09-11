import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from lib.time_series.diagnostics import calculate_acf, calculate_diagnostics


def test_acf_matches_hand_calculated_values():
    # Centered values [-1.5, -.5, .5, 1.5] have squared sum 5.
    # Lagged cross-product sums are 1.25, -1.5, -2.25.
    result = calculate_acf(pd.Series([1, 2, np.nan, 3, 4]), max_lag=10)
    np.testing.assert_allclose(result, [1, 0.25, -0.3, -0.45])
    assert result.index.tolist() == [0, 1, 2, 3]


@pytest.mark.parametrize("values", [[1, 1, 1], [1], [1, np.inf, 2]])
def test_acf_rejects_undefined_inputs(values):
    with pytest.raises(ValueError):
        calculate_acf(pd.Series(values))


def test_lag1_metric_matches_acf():
    series = pd.Series(np.random.default_rng(42).normal(size=100))
    assert calculate_diagnostics(series).lag1_autocorrelation == pytest.approx(
        calculate_acf(series).iloc[1]
    )


def test_acf_tab_renders_and_changes_inputs():
    def render_test_tab():
        import numpy as np
        import pandas as pd
        from unittest.mock import patch
        from views.dashboard_tabs.time_series_lab_tab import render

        prices = pd.DataFrame(
            {"Close": 100 * np.exp(np.cumsum(np.random.default_rng(42).normal(0, .01, 100)))},
            index=pd.bdate_range("2025-01-01", periods=100),
        )
        with patch("views.dashboard_tabs.time_series_lab_tab.get_price_data", return_value=prices):
            render({"ticker": "TEST"})

    app = AppTest.from_function(render_test_tab).run()
    assert not app.exception
    assert not app.error
    assert len(app.get("vega_lite_chart")) == 2
    assert "acf_max_lag=20" in app.code[0].value
    for transform in ["単純リターン", "対数リターン"]:
        app.selectbox[1].select(transform)
        app.slider[0].set_value(40)
        app.run()
        assert not app.exception
        assert not app.error
        assert "acf_max_lag=40" in app.code[0].value
