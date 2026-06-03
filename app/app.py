import streamlit as st

from pages.top_page import show_top_page
from pages.dashboard_page import show_dashboard_page


def init_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "top"

    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = None

    if "selected_company_name" not in st.session_state:
        st.session_state.selected_company_name = None


def main():
    st.set_page_config(page_title="個別株分析アプリ", layout="wide")

    init_session_state()

    if st.session_state.page == "top":
        show_top_page()
    elif st.session_state.page == "dashboard":
        show_dashboard_page()
    else:
        st.session_state.page = "top"
        show_top_page()


if __name__ == "__main__":
    main()
