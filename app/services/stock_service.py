from pathlib import Path

import pandas as pd
import streamlit as st
import yfinance as yf


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STOCK_MASTER_PATH = DATA_DIR / "stock_master.csv"


def load_stock_master() -> pd.DataFrame:
    if not STOCK_MASTER_PATH.exists():
        raise FileNotFoundError(f"銘柄マスタが存在しません: {STOCK_MASTER_PATH}")

    df = pd.read_csv(STOCK_MASTER_PATH)

    required_columns = {
        "ticker",
        "company_name",
        "industry",
        "sector",
        "is_active",
        "ir_url",
    }

    if not required_columns.issubset(df.columns):
        missing = sorted(required_columns - set(df.columns))
        raise ValueError(f"stock_master.csv に必須列がありません: {', '.join(missing)}")

    active_df = df[df["is_active"] == 1].copy()

    return active_df


def search_stocks(stock_master: pd.DataFrame, keyword: str) -> pd.DataFrame:
    if keyword is None or keyword.strip() == "":
        return stock_master

    keyword = keyword.strip()

    result = stock_master[
        stock_master["ticker"].astype(str).str.contains(keyword, case=False, na=False)
        | stock_master["company_name"]
        .astype(str)
        .str.contains(keyword, case=False, na=False)
    ]

    return result


@st.cache_data(ttl=900, show_spinner=False)
def get_price_data(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
) -> pd.DataFrame:
    stock = yf.Ticker(ticker)

    df = stock.history(period=period, interval=interval)

    if df.empty:
        raise ValueError(f"株価データを取得できませんでした: {ticker}")

    return df


@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_info(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    info = stock.info

    market_cap = info.get("marketCap")

    return {
        "industry": info.get("industry", "-"),
        "sector": info.get("sector", "-"),
        "market_cap": market_cap,
        "market_cap_text": format_yen_amount(market_cap),
        "currency": info.get("currency", "-"),
    }


def format_yen_amount(value) -> str:
    if value is None:
        return "-"

    try:
        value = float(value)
    except Exception:
        return "-"

    if value >= 1_0000_0000_0000:
        return f"{value / 1_0000_0000_0000:.1f}兆円"
    elif value >= 1_0000_0000:
        return f"{value / 1_0000_0000:.1f}億円"
    else:
        return f"{value:,.0f}円"
