import streamlit as st
import os
from dotenv import load_dotenv
from core.agent import EcommerceAIAgent
from ui.components import setup_page_config, create_sidebar, create_search_interface, display_results
from utils.explanations import generate_explanation
from utils import visualization

load_dotenv()

setup_page_config()

@st.cache_resource
def get_agent():
    return EcommerceAIAgent()

def main():
    create_sidebar()
    search_query, search_button = create_search_interface()
    
    if (search_button and search_query) or (st.session_state.get('search_query') and st.session_state.search_query != ""):
        if not search_query:
            search_query = st.session_state.search_query
            
        agent = get_agent()
        
        with st.spinner("🤖 Analyzing your data..."):
            result = agent.query_database(search_query)
        
        if result.get('error'):
            st.error(f"❌ Error: {result['error']}")
        else:
            st.session_state.current_results = result.get('results')
            st.session_state.current_query = search_query
            st.session_state.current_sql = result.get('sql')
            
            display_results(result, search_query, search_button, generate_explanation, visualization)

if __name__ == "__main__":
    main()
