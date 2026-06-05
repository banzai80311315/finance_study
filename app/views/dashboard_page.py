import importlib
import pkgutil

import streamlit as st

import views.dashboard_tabs as dashboard_tabs


def load_dashboard_tabs():
    tab_modules = []

    for module_info in pkgutil.iter_modules(dashboard_tabs.__path__):
        if module_info.name.startswith("_"):
            continue

        module = importlib.import_module(
            f"{dashboard_tabs.__name__}.{module_info.name}"
        )

        if hasattr(module, "TAB_NAME") and hasattr(module, "render"):
            tab_modules.append(module)

    tab_modules.sort(key=lambda module: getattr(module, "ORDER", 999))

    return tab_modules


def show_dashboard_page():
    ticker = st.session_state.get("selected_ticker")
    company_name = st.session_state.get("selected_company_name")

    if ticker is None:
        st.session_state.page = "top"
        st.rerun()

    st.title(f"{company_name} ダッシュボード")
    st.write(f"証券コード：{ticker}")

    if st.button("トップ画面へ戻る"):
        st.session_state.page = "top"
        st.rerun()

    st.divider()

    context = {
        "ticker": ticker,
        "company_name": company_name,
    }

    tab_modules = load_dashboard_tabs()
    tab_objects = st.tabs([module.TAB_NAME for module in tab_modules])

    for tab_object, tab_module in zip(tab_objects, tab_modules):
        with tab_object:
            tab_module.render(context)
