from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_top_page_renders_without_exception():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path)).run(timeout=20)

    assert not app.exception
    assert app.title[0].value == "Stock Research Studio"
    stock_table = app.dataframe[0].value
    assert "公式IR URL" in stock_table.columns
    assert stock_table["公式IR URL"].str.startswith("https://").all()
