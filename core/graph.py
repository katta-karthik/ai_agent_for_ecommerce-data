"""LangGraph orchestration graph for E-commerce AI Analytics Agent."""

import os
from typing import TypedDict, Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

from core.prompts import (
    SQL_PLANNING_SYSTEM_PROMPT,
    SQL_CORRECTION_SYSTEM_PROMPT,
    INSIGHT_GENERATION_SYSTEM_PROMPT,
)
from core.tools import execute_sql_query, DEFAULT_DB_PATH


# Pydantic Schemas for Structured Output
class QueryPlan(BaseModel):
    thought_process: str = Field(description="Reasoning about user question, tables needed, and metrics")
    sql: str = Field(description="Syntactically valid SQLite SELECT query, or empty string if no DB needed")
    needs_visualization: bool = Field(description="Whether the result would benefit from a graphical chart")
    visualization_type: Optional[Literal["bar", "line", "pie"]] = Field(
        default=None, description="Recommended chart type: 'bar' for rankings, 'line' for time trends, 'pie' for share"
    )


class SQLCorrection(BaseModel):
    thought_process: str = Field(description="Diagnosis of why the previous SQL failed and how to fix it")
    corrected_sql: str = Field(description="Corrected executable SQLite SELECT query")


class AgentInsight(BaseModel):
    answer: str = Field(description="Direct, concise answer with formatted numbers and key metric values")
    business_insight: str = Field(description="Business analyst interpretation of trends, drivers, proportions, or context")
    recommendations: Optional[str] = Field(default=None, description="Optional 1-2 actionable tips based on the data")


# LangGraph State Schema
class AgentState(TypedDict):
    question: str
    db_path: str
    plan: Optional[Dict[str, Any]]
    sql_query: str
    query_result: Optional[List[Dict[str, Any]]]
    columns: List[str]
    row_count: int
    error: Optional[str]
    retry_count: int
    answer: str
    business_insight: str
    recommendations: Optional[str]
    needs_visualization: bool
    visualization_type: Optional[str]
    steps: List[str]


def get_llm():
    """Factory to get available LLM: prefers Google Gemini if GOOGLE_API_KEY exists, else Groq."""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key and google_api_key != "your_gemini_api_key_here":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=google_api_key,
                temperature=0,
            )
        except Exception:
            pass

    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and groq_api_key != "your_groq_api_key_here":
        try:
            return ChatGroq(
                model_name="llama-3.1-8b-instant",
                temperature=0,
                groq_api_key=groq_api_key,
            )
        except Exception:
            pass

    return None


# Node 1: Analyze & Plan
def analyze_and_plan(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    steps = list(state.get("steps", []))
    steps.append(f"[ANALYZE] Question: '{question}'")
    
    llm = get_llm()
    if llm:
        try:
            structured_planner = llm.with_structured_output(QueryPlan)
            plan: QueryPlan = structured_planner.invoke([
                SystemMessage(content=SQL_PLANNING_SYSTEM_PROMPT),
                HumanMessage(content=f"User question: {question}")
            ])
            steps.append(f"[PLAN] {plan.thought_process}")
            steps.append(f"[SQL] {plan.sql}")
            return {
                "plan": plan.model_dump(),
                "sql_query": plan.sql,
                "needs_visualization": plan.needs_visualization,
                "visualization_type": plan.visualization_type,
                "steps": steps,
            }
        except Exception as e:
            steps.append(f"[WARN] Structured planning error ({str(e)}), using rule-based generator.")

    # Rule-based fallback if no LLM key or error
    q_lower = question.lower()
    sql = ""
    needs_viz = False
    viz_type = None

    if "total sales" in q_lower or "overall sales" in q_lower or "revenue" in q_lower:
        sql = "SELECT SUM(total_sales) as total_sales, SUM(total_units_ordered) as total_units FROM daily_sales;"
    elif "top" in q_lower and ("product" in q_lower or "item" in q_lower):
        sql = "SELECT item_id, total_lifetime_sales, total_lifetime_ad_sales, sales_rank FROM top_products_by_sales LIMIT 10;"
        needs_viz = True
        viz_type = "bar"
    elif "roas" in q_lower or "return on ad spend" in q_lower:
        sql = "SELECT item_id, avg_roas, total_ad_sales, total_ad_spend FROM best_roas_performance LIMIT 10;"
        needs_viz = True
        viz_type = "bar"
    elif "monthly" in q_lower or "trend" in q_lower or "over time" in q_lower or "daily" in q_lower:
        sql = "SELECT strftime('%Y-%m', date) as month, SUM(total_sales) as monthly_sales, SUM(total_units_ordered) as units FROM daily_sales GROUP BY month ORDER BY month;"
        needs_viz = True
        viz_type = "line"
    elif "cpc" in q_lower or "cost per click" in q_lower:
        sql = "SELECT item_id, avg_cpc, total_spend, total_clicks FROM cpc_analysis LIMIT 10;"
        needs_viz = True
        viz_type = "bar"
    elif "eligible" in q_lower:
        sql = "SELECT is_eligible, COUNT(*) as product_count FROM product_eligibility GROUP BY is_eligible;"
        needs_viz = True
        viz_type = "pie"
    elif "how many products" in q_lower or "product count" in q_lower:
        sql = "SELECT COUNT(*) as total_products, SUM(is_currently_eligible) as eligible_products FROM products;"
    else:
        sql = "SELECT item_id, total_lifetime_sales, total_lifetime_ad_sales FROM products ORDER BY total_lifetime_sales DESC LIMIT 10;"
        needs_viz = True
        viz_type = "bar"

    steps.append(f"[SQL] {sql}")
    return {
        "plan": {"thought_process": "Rule-based analysis", "sql": sql, "needs_visualization": needs_viz, "visualization_type": viz_type},
        "sql_query": sql,
        "needs_visualization": needs_viz,
        "visualization_type": viz_type,
        "steps": steps,
    }


# Node 2: Execute Query
def execute_query(state: AgentState) -> Dict[str, Any]:
    sql = state.get("sql_query", "")
    db_path = state.get("db_path", DEFAULT_DB_PATH)
    steps = list(state.get("steps", []))

    if not sql:
        steps.append("[WARN] No SQL query to execute.")
        return {
            "query_result": [],
            "columns": [],
            "row_count": 0,
            "error": "No SQL query provided.",
            "steps": steps,
        }

    steps.append("[EXEC] Executing query on SQLite database...")
    res = execute_sql_query(sql, db_path=db_path)

    if res["success"]:
        steps.append(f"[SUCCESS] Query executed successfully. Retrieved {res['row_count']} row(s).")
        return {
            "query_result": res["rows"],
            "columns": res["columns"],
            "row_count": res["row_count"],
            "error": None,
            "steps": steps,
        }
    else:
        steps.append(f"[ERROR] Query execution failed: {res['error']}")
        return {
            "query_result": [],
            "columns": [],
            "row_count": 0,
            "error": res["error"],
            "steps": steps,
        }


# Conditional Edge check for retry
def should_retry(state: AgentState) -> Literal["retry", "continue"]:
    error = state.get("error")
    retry_count = state.get("retry_count", 0)
    if error and retry_count < 2:
        return "retry"
    return "continue"


# Node 3: Correct SQL
def correct_sql(state: AgentState) -> Dict[str, Any]:
    previous_sql = state.get("sql_query", "")
    error_msg = state.get("error", "Unknown error")
    retry_count = state.get("retry_count", 0) + 1
    steps = list(state.get("steps", []))
    steps.append(f"[RETRY] Correcting SQL (Attempt {retry_count} of 2) following error: {error_msg}")

    llm = get_llm()
    corrected_sql = previous_sql
    if llm:
        try:
            structured_fixer = llm.with_structured_output(SQLCorrection)
            fix: SQLCorrection = structured_fixer.invoke([
                SystemMessage(content=SQL_CORRECTION_SYSTEM_PROMPT),
                HumanMessage(content=f"Original Question: {state['question']}\nFailed SQL: {previous_sql}\nError: {error_msg}")
            ])
            corrected_sql = fix.corrected_sql
            steps.append(f"[DIAGNOSE] {fix.thought_process}")
            steps.append(f"[SQL_FIXED] {corrected_sql}")
        except Exception as e:
            steps.append(f"[WARN] SQL correction model error: {str(e)}")

    return {
        "sql_query": corrected_sql,
        "retry_count": retry_count,
        "steps": steps,
    }


# Node 4: Synthesize Insight
def synthesize_insight(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    rows = state.get("query_result", [])
    row_count = state.get("row_count", 0)
    sql = state.get("sql_query", "")
    error = state.get("error")
    steps = list(state.get("steps", []))
    steps.append("[SYNTHESIZE] Synthesizing business insight from data...")

    if error:
        return {
            "answer": f"Unable to retrieve data due to database error: {error}",
            "business_insight": "Please refine your question or verify the requested table columns.",
            "recommendations": None,
            "steps": steps,
        }

    if row_count == 0 or not rows:
        return {
            "answer": "No matching data was found for this question.",
            "business_insight": "The query executed successfully, but returned 0 records matching the criteria.",
            "recommendations": "Try broadening the date filter or checking if the item ID exists.",
            "steps": steps,
        }

    llm = get_llm()
    if llm:
        try:
            structured_insight = llm.with_structured_output(AgentInsight)
            sample_data = str(rows[:10])
            insight: AgentInsight = structured_insight.invoke([
                SystemMessage(content=INSIGHT_GENERATION_SYSTEM_PROMPT),
                HumanMessage(content=f"Question: {question}\nExecuted SQL: {sql}\nRow Count: {row_count}\nResults Sample: {sample_data}")
            ])
            steps.append("[INSIGHT] Generated business insight and recommendations.")
            return {
                "answer": insight.answer,
                "business_insight": insight.business_insight,
                "recommendations": insight.recommendations,
                "steps": steps,
            }
        except Exception as e:
            steps.append(f"[WARN] Insight synthesis error ({str(e)}), generating standard response.")

    # Rule-based fallback synthesis
    first_row = rows[0]
    if row_count == 1:
        details = ", ".join([f"{k.replace('_', ' ').title()}: {v:,.2f}" if isinstance(v, (int, float)) else f"{k.replace('_', ' ').title()}: {v}" for k, v in first_row.items()])
        answer = f"Found single record: {details}."
        insight_text = "This metric represents the aggregated performance across the dataset."
    else:
        answer = f"Found {row_count} matching records for your question."
        first_keys = list(first_row.keys())
        first_metric = first_keys[1] if len(first_keys) > 1 else first_keys[0]
        insight_text = f"Top entry is Item {first_row.get('item_id', 'N/A')} with {first_metric.replace('_', ' ').title()} of {first_row.get(first_metric, 'N/A')}."

    return {
        "answer": answer,
        "business_insight": insight_text,
        "recommendations": "Review high-performing items to scale advertising campaigns.",
        "steps": steps,
    }


# Graph Builder
def create_analytics_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("analyze_and_plan", analyze_and_plan)
    workflow.add_node("execute_query", execute_query)
    workflow.add_node("correct_sql", correct_sql)
    workflow.add_node("synthesize_insight", synthesize_insight)

    # Add Edges
    workflow.add_edge(START, "analyze_and_plan")
    workflow.add_edge("analyze_and_plan", "execute_query")
    workflow.add_conditional_edges(
        "execute_query",
        should_retry,
        {
            "retry": "correct_sql",
            "continue": "synthesize_insight",
        }
    )
    workflow.add_edge("correct_sql", "execute_query")
    workflow.add_edge("synthesize_insight", END)

    return workflow.compile()
