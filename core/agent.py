"""E-commerce AI Analytics Agent orchestrated with LangGraph."""

import os
import pandas as pd
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from core.graph import create_analytics_graph
from core.tools import (
    execute_sql_query,
    get_database_schema,
    get_sales_kpi_summary,
    DEFAULT_DB_PATH,
)


class EcommerceAIAgent:
    """Agentic AI Data Analyst powered by LangGraph, LangChain, and SQLite."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        load_dotenv()
        self.db_path = db_path
        self.graph = create_analytics_graph()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        if self.google_api_key:
            print("[INFO] Active LLM Provider: Google Gemini (gemini-2.5-flash)")
        elif self.groq_api_key:
            print("[INFO] Active LLM Provider: Groq (llama-3.1-8b-instant)")
        else:
            print("[NOTICE] No LLM API key found in .env (GOOGLE_API_KEY or GROQ_API_KEY).")
            print("         Using built-in SQL planning rules until an API key is configured.")

    def run(self, question: str, custom_api_key: Optional[str] = None, *args, **kwargs) -> Dict[str, Any]:
        """Execute the full LangGraph agent workflow for an analytical question."""
        api_key = custom_api_key or kwargs.get("api_key") or kwargs.get("custom_key")
        initial_state = {
            "question": question,
            "db_path": self.db_path,
            "plan": None,
            "sql_query": "",
            "query_result": None,
            "columns": [],
            "row_count": 0,
            "error": None,
            "retry_count": 0,
            "answer": "",
            "business_insight": "",
            "recommendations": None,
            "needs_visualization": False,
            "visualization_type": None,
            "steps": [],
            "api_key": api_key,
        }

        try:
            final_state = self.graph.invoke(initial_state)
            
            rows = final_state.get("query_result", [])
            df = pd.DataFrame(rows) if rows else pd.DataFrame()

            return {
                "question": question,
                "answer": final_state.get("answer", "Analysis complete."),
                "business_insight": final_state.get("business_insight", ""),
                "recommendations": final_state.get("recommendations"),
                "sql": final_state.get("sql_query", ""),
                "results": df,
                "row_count": final_state.get("row_count", len(df)),
                "needs_visualization": final_state.get("needs_visualization", False),
                "visualization_type": final_state.get("visualization_type"),
                "steps": final_state.get("steps", []),
                "error": final_state.get("error"),
            }
        except Exception as e:
            return {
                "question": question,
                "answer": "An unexpected error occurred during analysis.",
                "business_insight": "",
                "recommendations": None,
                "sql": "",
                "results": pd.DataFrame(),
                "row_count": 0,
                "needs_visualization": False,
                "visualization_type": None,
                "steps": [f"❌ Pipeline exception: {str(e)}"],
                "error": str(e),
            }

    def query_database(self, question: str, *args, **kwargs) -> Dict[str, Any]:
        """Backward-compatible method matching original repository interface."""
        return self.run(question, *args, **kwargs)

    def get_schema(self) -> str:
        """Inspect database structure."""
        return get_database_schema(self.db_path)

    def get_summary(self) -> Dict[str, Any]:
        """Retrieve key business KPIs."""
        return get_sales_kpi_summary(self.db_path)
