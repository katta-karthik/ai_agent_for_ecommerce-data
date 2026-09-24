"""Streamlit entry point for E-commerce AI Analytics Agent."""

import streamlit as st
from dotenv import load_dotenv
from core.agent import EcommerceAIAgent
from ui.components import setup_page_config, create_sidebar, create_search_interface, display_results
from utils import visualization

load_dotenv()

setup_page_config()


@st.cache_resource
def get_agent():
    return EcommerceAIAgent()


def main():
    create_sidebar()
    search_query, search_button = create_search_interface()

    # Determine if we should trigger analysis
    should_run = False
    query_to_run = ""

    if search_button and search_query.strip():
        query_to_run = search_query.strip()
        should_run = True
    elif st.session_state.get("search_query") and st.session_state.search_query != st.session_state.get("last_executed_query"):
        query_to_run = st.session_state.search_query.strip()
        should_run = True

    if should_run and query_to_run:
        agent = get_agent()
        with st.spinner("🤖 AI Analyst is reasoning, generating SQL, and analyzing SQLite data..."):
            result = agent.run(query_to_run)
            st.session_state.current_result_obj = result
            st.session_state.last_executed_query = query_to_run

    if st.session_state.get("current_result_obj"):
        display_results(
            st.session_state.current_result_obj,
            st.session_state.get("last_executed_query", ""),
            visualization
        )


if __name__ == "__main__":
    main()
