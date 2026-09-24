"""Streamlit UI components for E-commerce AI Analytics Agent."""

import streamlit as st
import time
from core.tools import get_sales_kpi_summary


def setup_page_config():
    st.set_page_config(
        page_title="E-commerce AI Analytics — Agentic Data Analyst",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )


MAX_SESSION_QUERIES = 3


def create_sidebar():
    with st.sidebar:
        st.title("🛒 Agentic Analytics")
        st.caption("Powered by **LangGraph** & **SQLite**")

        # Quota Protection Status
        st.markdown("### 🛡️ Quota Protection")
        queries_used = st.session_state.get("queries_used", 0)
        custom_key = st.session_state.get("custom_api_key", "").strip()

        if custom_key:
            st.success("🔑 Personal API Key active — Unlimited queries")
        else:
            remaining = max(0, MAX_SESSION_QUERIES - queries_used)
            if remaining > 0:
                st.info(f"📊 **{remaining} of {MAX_SESSION_QUERIES} queries left**")
            else:
                st.warning("⚠️ **Session limit reached (3/3 used)**")
            st.caption("Rate-limits queries per visitor session to protect shared host token budget.")

        with st.expander("🔑 Use Your Own API Key (Optional)", expanded=False):
            key_input = st.text_input(
                "Gemini or Groq API Key:",
                type="password",
                value=st.session_state.get("custom_api_key", ""),
                help="Enter your own key to bypass the demo session quota.",
                key="custom_api_key_input"
            )
            if key_input and key_input != st.session_state.get("custom_api_key", ""):
                st.session_state.custom_api_key = key_input.strip()
                st.rerun()

        if st.session_state.get("queries_used", 0) > 0 and not custom_key:
            if st.button("🔄 Reset Query Count", use_container_width=True):
                st.session_state.queries_used = 0
                st.rerun()

        st.divider()

        # Live Dataset Overview
        try:
            summary = get_sales_kpi_summary()
            if "error" not in summary:
                st.markdown("### 📈 Store Snapshot")
                col_a, col_b = st.columns(2)
                col_a.metric("Total Sales", f"${summary['total_sales_usd']:,.0f}")
                col_b.metric("Blended ROAS", f"{summary['blended_roas']}x")
                col_c, col_d = st.columns(2)
                col_c.metric("Active Products", f"{summary['total_products']}")
                col_d.metric("Units Ordered", f"{summary['total_units_ordered']:,}")
                st.caption(f"📅 Dates: {summary['date_range']}")
                st.divider()
        except Exception:
            pass

        st.markdown("### 📊 Demo Questions")
        demo_questions = [
            "What is my total sales?",
            "Show monthly sales trend",
            "Which products generated the highest revenue?",
            "What is the average Return on Ad Spend (ROAS)?",
            "Show products with the highest click-through rate",
        ]

        for q in demo_questions:
            if st.button(q, key=f"demo_{q}", use_container_width=True):
                st.session_state.search_query = q
                st.rerun()

        st.markdown("### 🔍 Suggested Questions")
        suggested_questions = [
            "Show me the top 10 products by total sales",
            "What are the best performing products by ROAS?",
            "Show me products with the lowest CPC",
            "How many products are eligible for advertising?",
            "What is the daily sales breakdown over time?",
            "Compare ad sales versus organic sales"
        ]

        for q in suggested_questions:
            if st.button(q, key=f"suggested_{q}", use_container_width=True):
                st.session_state.search_query = q
                st.rerun()

        st.divider()
        st.markdown("### 🛠️ Architecture")
        st.markdown(
            """
            - **Orchestration**: LangGraph StateGraph
            - **Tools**: Safe Read-Only SQL, Schema, KPIs
            - **Correction**: Automatic SQL Retry Loop
            - **Protocol**: MCP Analytical Server
            """
        )


def create_search_interface():
    st.title("🛒 E-commerce AI Analytics")
    st.markdown("*Ask any business or analytics question in natural language. The LangGraph agent plans, validates, executes SQL, and generates insights.*")

    queries_used = st.session_state.get("queries_used", 0)
    custom_key = st.session_state.get("custom_api_key", "").strip()
    remaining = max(0, MAX_SESSION_QUERIES - queries_used)

    if not custom_key:
        if remaining > 0:
            st.caption(f"⚡ Live Demo Quota: **{remaining} of {MAX_SESSION_QUERIES} queries remaining** in this session.")
        else:
            st.warning("⚠️ **Session limit reached (3/3 queries used).** Live queries are paused for this session to preserve token quota. You can still click the pre-set demo questions on the left or add a personal API key in the sidebar.")

    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""

        search_query = st.text_input(
            "Ask a question about your e-commerce data:",
            value=st.session_state.search_query,
            placeholder="e.g., Which products generated the highest revenue?",
            key="main_search"
        )

        col_search, col_clear = st.columns([3, 1])

        with col_search:
            search_button = st.button("🚀 Analyze with Agent", use_container_width=True, type="primary")

        with col_clear:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.search_query = ""
                st.session_state.current_results = None
                st.session_state.current_result_obj = None
                st.rerun()

    return search_query, search_button


def display_results(result, search_query, viz_func):
    """Render the AI Data Analyst response card."""
    if not result:
        return

    # Check for error
    if result.get("error"):
        st.error(f"❌ Analysis Failed: {result['error']}")
        if result.get("steps"):
            with st.expander("🤖 Agent Steps (Debug Trace)", expanded=True):
                for s in result["steps"]:
                    st.write(s)
        return

    # 1. Answer Card
    st.markdown("### 💡 Answer")
    st.info(result.get("answer", "Analysis completed."))

    # 2. Business Insight
    if result.get("business_insight"):
        st.markdown("### 📈 Business Insight")
        st.success(result["business_insight"])

    # 3. Recommendations (if available)
    if result.get("recommendations"):
        st.markdown("### 🎯 Recommendations")
        st.markdown(f"> {result['recommendations']}")

    # 4. Collapsible Agent Execution Steps
    if result.get("steps"):
        with st.expander("🤖 View Agent Analysis & Reasoning Steps (LangGraph Trace)", expanded=False):
            for step in result["steps"]:
                st.write(step)

    # 5. Collapsible SQL Query
    if result.get("sql"):
        with st.expander("🔍 View Generated SQL Query", expanded=False):
            st.code(result["sql"], language="sql")

    # 6. Data Results
    df = result.get("results")
    if df is not None and not df.empty:
        st.markdown(f"#### 📋 Query Results ({len(df)} rows)")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 7. Visualization
        viz_options = viz_func.get_visualization_options(df)
        if viz_options:
            st.markdown("#### 📊 Visualization")

            # Default to agent's suggested viz type if available
            recommended = result.get("visualization_type", "")
            default_index = 0
            if recommended:
                for idx, opt in enumerate(viz_options):
                    if recommended.lower() in opt.lower():
                        default_index = idx
                        break

            col_viz, _ = st.columns([2, 3])
            with col_viz:
                selected_viz = st.selectbox(
                    "Chart Type:",
                    options=viz_options,
                    index=default_index,
                    key="viz_selector"
                )

            if selected_viz:
                chart = viz_func.create_visualization(df, selected_viz)
                if chart:
                    st.pyplot(chart, use_container_width=True)
                    import matplotlib.pyplot as plt
                    plt.close(chart)
        else:
            if len(df) == 1:
                st.caption("ℹ️ Single aggregate value displayed above. Graphical chart unnecessary.")
    else:
        st.warning("No records matched your criteria.")
