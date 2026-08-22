import streamlit as st

from services.stock_service import load_stock_master, search_stocks


def show_top_page():
    st.title("Stock Research Studio")
    st.caption("企業・価格・リスク・時系列モデルを一つの場所で検証する個別株研究環境")

    try:
        stock_master = load_stock_master()
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"銘柄一覧を読み込めませんでした: {exc}")
        return

    overview1, overview2, overview3 = st.columns(3)
    overview1.metric("登録銘柄", f"{len(stock_master)}社")
    overview2.metric("分析機能", "5タブ")
    overview3.metric("検証方式", "Rolling origin")

    st.header("銘柄を選ぶ")

    keyword = st.text_input("銘柄名・証券コードで検索")

    if st.button("検索"):
        st.session_state.search_keyword = keyword

    filtered_stocks = search_stocks(
        stock_master, st.session_state.get("search_keyword", "")
    )

    st.subheader("銘柄一覧")

    display_columns = {
        "ticker": "証券コード",
        "company_name": "銘柄名",
        "industry": "業種",
        "sector": "セクター",
        "ir_url": "公式IR URL",
    }
    st.dataframe(
        filtered_stocks[list(display_columns)].rename(columns=display_columns),
        width="stretch",
        hide_index=True,
        column_config={
            "公式IR URL": st.column_config.LinkColumn(
                "公式IR URL",
                help="企業公式の株主・投資家情報ページを開きます。",
            )
        },
    )

    if filtered_stocks.empty:
        st.warning("該当する銘柄がありません。")
        return

    options = filtered_stocks.assign(
        label=lambda frame: frame["company_name"] + "（" + frame["ticker"] + "）"
    )
    selected_label = st.selectbox(
        "分析する銘柄を選択", options["label"].tolist()
    )

    if st.button("分析開始"):
        selected_row = options[options["label"] == selected_label].iloc[0]

        st.session_state.selected_ticker = selected_row["ticker"]
        st.session_state.selected_company_name = selected_row["company_name"]
        st.session_state.page = "dashboard"

        st.rerun()
