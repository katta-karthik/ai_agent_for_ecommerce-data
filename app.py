"""Streamlit entry point for E-commerce AI Analytics Agent."""

import streamlit as st
from dotenv import load_dotenv
from core.agent import EcommerceAIAgent
from ui.components import (
    setup_page_config,
    create_sidebar,
    create_search_interface,
    display_results,
    MAX_SESSION_QUERIES,
)
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
        queries_used = st.session_state.get("queries_used", 0)
        custom_key = st.session_state.get("custom_api_key", "").strip()

        # Enforce rate limit for shared host key
        if not custom_key and queries_used >= MAX_SESSION_QUERIES:
            st.warning(
                f"🛑 **Session Query Limit Reached ({MAX_SESSION_QUERIES}/{MAX_SESSION_QUERIES} queries used)**\n\n"
                "To ensure all recruiters and hiring managers can test this portfolio application throughout the month without exhausting the shared free API quota, live queries are capped at 3 per visitor session.\n\n"
                "**How to continue testing:**\n"
                "- 📌 Explore the pre-computed **Demo Questions** on the left.\n"
                "- 🔑 Provide a free Gemini API key in the sidebar for unlimited queries.\n"
                "- 🔄 Or click **Reset Query Count** in the sidebar."
            )
        else:
            agent = get_agent()
            with st.spinner("🤖 AI Analyst is reasoning, generating SQL, and analyzing SQLite data..."):
                result = agent.run(query_to_run, custom_api_key=custom_key if custom_key else None)
                st.session_state.current_result_obj = result
                st.session_state.last_executed_query = query_to_run
                if not custom_key:
                    st.session_state.queries_used = queries_used + 1

    if st.session_state.get("current_result_obj"):
        display_results(
            st.session_state.current_result_obj,
            st.session_state.get("last_executed_query", ""),
            visualization
        )


if __name__ == "__main__":
    main()
