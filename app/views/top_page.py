import streamlit as st

from services.stock_service import load_stock_master, search_stocks


def show_top_page():
    st.title("個別株分析アプリ")

    st.header("銘柄検索")

    stock_master = load_stock_master()

    keyword = st.text_input("銘柄名・証券コードで検索")

    if st.button("検索"):
        st.session_state.search_keyword = keyword

    filtered_stocks = search_stocks(
        stock_master, st.session_state.get("search_keyword", "")
    )

    st.subheader("銘柄一覧")

    st.dataframe(filtered_stocks, width="stretch")

    if filtered_stocks.empty:
        st.warning("該当する銘柄がありません。")
        return

    selected_company_name = st.selectbox(
        "分析する銘柄を選択", filtered_stocks["company_name"].tolist()
    )

    if st.button("分析開始"):
        selected_row = filtered_stocks[
            filtered_stocks["company_name"] == selected_company_name
        ].iloc[0]

        st.session_state.selected_ticker = selected_row["ticker"]
        st.session_state.selected_company_name = selected_row["company_name"]
        st.session_state.page = "dashboard"

        st.rerun()
