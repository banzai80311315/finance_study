import streamlit as st
import pandas as pd
import numpy as np


# =========================
# ページ設定
# =========================
st.set_page_config(page_title="個別株分析アプリ", layout="wide")


# =========================
# モックデータ
# =========================
stocks = pd.DataFrame({
    "証券コード": ["9531.T", "9501.T", "9505.T", "7203.T"],
    "銘柄名": ["東京ガス", "東京電力HD", "北陸電力", "トヨタ自動車"],
    "業種": ["ガス", "電気", "電気", "輸送用機器"],
    "セクター": ["公益事業", "公益事業", "公益事業", "一般消費財"],
})

favorite_stocks = ["東京ガス", "北陸電力"]

dates = pd.date_range("2025-01-01", periods=120)

mock_price = pd.DataFrame({
    "日付": dates,
    "終値": np.cumsum(np.random.randn(120)) + 2500,
    "出来高": np.random.randint(500000, 3000000, size=120),
})

dividend_df = pd.DataFrame({
    "年度": ["2021", "2022", "2023", "2024", "2025"],
    "配当": [55, 60, 65, 70, 75],
})


# =========================
# セッション管理
# =========================
if "page" not in st.session_state:
    st.session_state.page = "top"

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = None


# =========================
# トップ画面
# =========================
def show_top_page():
    st.title("個別株分析アプリ")

    st.header("銘柄検索")

    keyword = st.text_input("銘柄名・証券コードで検索")

    if keyword:
        filtered = stocks[
            stocks["銘柄名"].str.contains(keyword, case=False, na=False)
            | stocks["証券コード"].str.contains(keyword, case=False, na=False)
        ]
    else:
        filtered = stocks

    st.subheader("お気に入り銘柄")

    for name in favorite_stocks:
        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(f"☆ {name}")

        with col2:
            if st.button("選択", key=f"fav_{name}"):
                st.session_state.selected_stock = stocks[stocks["銘柄名"] == name].iloc[
                    0
                ]
                st.session_state.page = "dashboard"
                st.rerun()

    st.subheader("銘柄一覧")

    st.dataframe(filtered, use_container_width=True)

    selected_name = st.selectbox("分析する銘柄を選択", filtered["銘柄名"].tolist())

    if st.button("分析開始"):
        st.session_state.selected_stock = stocks[
            stocks["銘柄名"] == selected_name
        ].iloc[0]
        st.session_state.page = "dashboard"
        st.rerun()


# =========================
# ダッシュボード画面
# =========================
def show_dashboard_page():
    stock = st.session_state.selected_stock

    if stock is None:
        st.session_state.page = "top"
        st.rerun()

    st.title(f"{stock['銘柄名']} ダッシュボード")

    col1, col2 = st.columns([5, 1])

    with col1:
        st.write(f"証券コード：{stock['証券コード']}")

    with col2:
        st.button("☆ お気に入り")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["基本情報", "株価分析", "財務分析", "配当分析"])

    # -------------------------
    # タブ1：基本情報
    # -------------------------
    with tab1:
        st.header("基本情報")

        col1, col2, col3 = st.columns(3)

        col1.metric("銘柄名", stock["銘柄名"])
        col2.metric("証券コード", stock["証券コード"])
        col3.metric("業種", stock["業種"])

        col4, col5, col6 = st.columns(3)

        col4.metric("セクター", stock["セクター"])
        col5.metric("時価総額", "2.1兆円")
        col6.metric("発行済株式数", "8億株")

    # -------------------------
    # タブ2：株価分析
    # -------------------------
    with tab2:
        st.header("株価分析")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("現在株価", "2,520円")
        col2.metric("前日終値", "2,500円")
        col3.metric("高値", "2,560円")
        col4.metric("安値", "2,480円")

        st.subheader("株価チャート")
        st.line_chart(mock_price.set_index("日付")["終値"])

        st.subheader("出来高チャート")
        st.bar_chart(mock_price.set_index("日付")["出来高"])

    # -------------------------
    # タブ3：財務分析
    # -------------------------
    with tab3:
        st.header("財務分析")

        st.subheader("収益性")

        col1, col2, col3 = st.columns(3)

        col1.metric("売上高", "2.6兆円")
        col2.metric("営業利益", "1,800億円")
        col3.metric("当期純利益", "1,200億円")

        st.subheader("安全性")

        col4, col5, col6 = st.columns(3)

        col4.metric("総資産", "3.8兆円")
        col5.metric("自己資本", "1.7兆円")
        col6.metric("自己資本比率", "44.7%")

        st.subheader("1株あたり指標・効率性")

        col7, col8, col9, col10 = st.columns(4)

        col7.metric("ROE", "7.1%")
        col8.metric("ROA", "3.1%")
        col9.metric("EPS", "320円")
        col10.metric("BPS", "4,200円")

        st.subheader("バリュエーション")

        col11, col12 = st.columns(2)

        col11.metric("PER", "8.2倍")
        col12.metric("PBR", "0.6倍")

    # -------------------------
    # タブ4：配当分析
    # -------------------------
    with tab4:
        st.header("配当分析")

        col1, col2, col3 = st.columns(3)

        col1.metric("配当利回り", "3.2%")
        col2.metric("直近配当", "75円")
        col3.metric("配当成長率", "8.3%")

        st.subheader("配当履歴チャート")
        st.bar_chart(dividend_df.set_index("年度")["配当"])

    st.divider()

    if st.button("トップ画面へ戻る"):
        st.session_state.page = "top"
        st.rerun()


# =========================
# 画面制御
# =========================
if st.session_state.page == "top":
    show_top_page()
else:
    show_dashboard_page()
