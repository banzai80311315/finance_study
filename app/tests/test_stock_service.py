import pandas as pd

from services.stock_service import search_stocks


def test_search_stocks_matches_ticker_and_company_name():
    stocks = pd.DataFrame(
        {"ticker": ["9432.T", "9501.T"], "company_name": ["NTT", "東京電力HD"]}
    )

    assert search_stocks(stocks, "9432")["company_name"].tolist() == ["NTT"]
    assert search_stocks(stocks, "東京")["ticker"].tolist() == ["9501.T"]
