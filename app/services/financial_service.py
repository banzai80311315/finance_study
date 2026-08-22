import yfinance as yf
import streamlit as st

from services.stock_service import format_yen_amount


@st.cache_data(ttl=3600, show_spinner=False)
def get_financial_summary(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    info = stock.info

    financials = stock.financials
    balance_sheet = stock.balance_sheet

    revenue = get_statement_value(financials, "Total Revenue")
    operating_income = get_statement_value(financials, "Operating Income")
    net_income = get_statement_value(financials, "Net Income")

    total_assets = get_statement_value(balance_sheet, "Total Assets")

    equity = get_first_available_statement_value(
        balance_sheet,
        [
            "Stockholders Equity",
            "Total Equity Gross Minority Interest",
            "Common Stock Equity",
        ],
    )

    per = info.get("trailingPE")
    pbr = info.get("priceToBook")
    roe = info.get("returnOnEquity")
    market_cap = info.get("marketCap")

    return {
        "revenue": revenue,
        "revenue_text": format_yen_amount(revenue),
        "operating_income": operating_income,
        "operating_income_text": format_yen_amount(operating_income),
        "net_income": net_income,
        "net_income_text": format_yen_amount(net_income),
        "total_assets": total_assets,
        "total_assets_text": format_yen_amount(total_assets),
        "equity": equity,
        "equity_text": format_yen_amount(equity),
        "per": per,
        "per_text": format_multiple(per),
        "pbr": pbr,
        "pbr_text": format_multiple(pbr),
        "roe": roe,
        "roe_text": format_percent(roe),
        "market_cap": market_cap,
        "market_cap_text": format_yen_amount(market_cap),
    }


def get_statement_value(statement, row_name: str):
    if statement is None or statement.empty:
        return None

    if row_name not in statement.index:
        return None

    series = statement.loc[row_name]

    if series.empty:
        return None

    value = series.iloc[0]

    if value != value:
        return None

    return value


def get_first_available_statement_value(statement, row_names: list[str]):
    for row_name in row_names:
        value = get_statement_value(statement, row_name)

        if value is not None:
            return value

    return None


def format_multiple(value) -> str:
    if value is None:
        return "-"

    try:
        return f"{float(value):.2f}倍"
    except Exception:
        return "-"


def format_percent(value) -> str:
    if value is None:
        return "-"

    try:
        return f"{float(value) * 100:.2f}%"
    except Exception:
        return "-"
