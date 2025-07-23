import streamlit as st
import time

def setup_page_config():
    st.set_page_config(
        page_title="E-commerce AI Analytics",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def create_sidebar():
    with st.sidebar:
        st.title("🛒 Questions")
        
        st.markdown("### 📊 Demo Questions")
        demo_questions = [
            "What is my total sales?",
            "Calculate the average Return on Ad Spend", 
            "Which products have the highest click-through rate?",
        ]
        
        for q in demo_questions:
            if st.button(q, key=f"demo_{q}", use_container_width=True):
                st.session_state.search_query = q
        
        st.markdown("### 🔍 Suggested Questions")
        suggested_questions = [
            "Show me the top 10 products by total sales",
            "Which products have sales over $50,000?",
            "What are the 5 best performing ads by RoAS?",
            "Show me products with the lowest CPC",
            "Which products are eligible for advertising?",
            "Show me the worst performing products",
            "What is the average revenue per product?",
            "Show me products with highest lifetime sales"
        ]
        
        for q in suggested_questions:
            if st.button(q, key=f"suggested_{q}", use_container_width=True):
                st.session_state.search_query = q

def create_search_interface():
    st.title("🛒 E-commerce AI Analytics")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""
        
        search_query = st.text_input(
            "Ask a question about your e-commerce data:",
            value=st.session_state.search_query,
            placeholder="e.g., What are my top selling products?",
            key="main_search"
        )
        
        col_search, col_clear = st.columns([2, 1])
        
        with col_search:
            search_button = st.button("🔍 Search", use_container_width=True, type="primary")
        
        with col_clear:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.search_query = ""
                st.rerun()
    
    return search_query, search_button

def stream_text(text, placeholder):
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(0.02)

def display_results(result, search_query, search_button, explanation_func, viz_func):
    response_placeholder = st.empty()
    
    if result.get('results') is not None and not result['results'].empty:
        df = result['results']
        explanation = explanation_func(df, search_query)
        
        if search_button or 'last_streamed_query' not in st.session_state or st.session_state.last_streamed_query != search_query:
            stream_text(explanation, response_placeholder)
            st.session_state.last_streamed_query = search_query
        else:
            response_placeholder.markdown(explanation)
        
        with st.expander("🔍 View Generated SQL Query"):
            st.code(result['sql'], language='sql')
        
        st.markdown("#### 📋 Results")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        viz_options = viz_func.get_visualization_options(df)
        
        if viz_options:
            st.markdown("#### 📊 Visualization")
            
            col_viz, col_empty = st.columns([2, 3])
            
            with col_viz:
                selected_viz = st.selectbox(
                    "Choose visualization type:",
                    options=viz_options,
                    index=0,
                    key="viz_selector"
                )
            
            if selected_viz:
                chart = viz_func.create_visualization(df, selected_viz)
                if chart:
                    st.pyplot(chart, use_container_width=True)
                    import matplotlib.pyplot as plt
                    plt.close(chart)
                else:
                    st.info(f"Unable to create {selected_viz}.")
        else:
            st.info("This data is best displayed in table format.")
    
    else:
        stream_text("No results found. Try a different query.", response_placeholder)
