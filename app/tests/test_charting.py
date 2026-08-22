import pandas as pd

from lib.charting import padded_domain


def test_padded_domain_uses_minimum_and_maximum_across_all_series():
    data = pd.DataFrame({"A": [100, 120], "B": [90, 130]})

    assert padded_domain(data) == (80.0, 140.0)


def test_padded_domain_ignores_missing_values():
    data = pd.Series([float("nan"), 5.0, 15.0])

    assert padded_domain(data) == (-5.0, 25.0)
