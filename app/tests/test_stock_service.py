import pandas as pd

from services.stock_service import load_stock_master, search_stocks


def test_search_stocks_matches_ticker_and_company_name():
    stocks = pd.DataFrame(
        {"ticker": ["9432.T", "9501.T"], "company_name": ["NTT", "東京電力HD"]}
    )

    assert search_stocks(stocks, "9432")["company_name"].tolist() == ["NTT"]
    assert search_stocks(stocks, "東京")["ticker"].tolist() == ["9501.T"]


def test_every_active_stock_has_an_official_ir_url():
    stocks = load_stock_master()

    assert stocks["ir_url"].notna().all()
    assert stocks["ir_url"].str.startswith("https://").all()
