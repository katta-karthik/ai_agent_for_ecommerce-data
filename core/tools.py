"""Database inspection, analytical execution, and reporting tools."""

import sqlite3
import re
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool

DEFAULT_DB_PATH = "ecommerce_optimized.db"

FORBIDDEN_SQL_PATTERNS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bPRAGMA\b",
    r"\bREPLACE\b",
]


def validate_read_only_sql(query: str) -> Optional[str]:
    """Ensure the SQL query is read-only and safe to execute.
    
    Returns None if valid, or an error message if invalid.
    """
    cleaned = query.strip()
    if not cleaned:
        return "Query cannot be empty."

    # Remove comments
    cleaned = re.sub(r"--.*$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL).strip()

    # Must start with SELECT or WITH
    upper_query = cleaned.upper()
    if not (upper_query.startswith("SELECT") or upper_query.startswith("WITH")):
        return "Security Violation: Only SELECT or WITH (Common Table Expression) queries are permitted."

    # Check for forbidden keywords
    for pattern in FORBIDDEN_SQL_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return f"Security Violation: Query contains prohibited keyword matching '{pattern}'."

    # Prevent multiple semicolon-delimited statements
    statements = [s.strip() for s in cleaned.split(";") if s.strip()]
    if len(statements) > 1:
        return "Security Violation: Multiple SQL statements are not allowed."

    return None


def execute_sql_query(query: str, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Execute a read-only SQL query against the SQLite database.
    
    Returns a dictionary with:
      - success (bool)
      - rows (List[Dict[str, Any]])
      - columns (List[str])
      - row_count (int)
      - error (Optional[str])
    """
    validation_error = validate_read_only_sql(query)
    if validation_error:
        return {
            "success": False,
            "rows": [],
            "columns": [],
            "row_count": 0,
            "error": validation_error,
        }

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        rows_raw = cursor.fetchall()
        
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = [dict(row) for row in rows_raw]
        conn.close()

        return {
            "success": True,
            "rows": rows,
            "columns": columns,
            "row_count": len(rows),
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "rows": [],
            "columns": [],
            "row_count": 0,
            "error": f"SQLite execution error: {str(e)}",
        }


def get_database_schema(db_path: str = DEFAULT_DB_PATH) -> str:
    """Retrieve full SQLite schema info including tables, views, and columns."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, type, sql FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%'")
        items = cursor.fetchall()
        
        schema_lines = ["# Database Schema & Structure\n"]
        for name, item_type, sql in items:
            schema_lines.append(f"### {item_type.upper()}: `{name}`")
            if sql:
                schema_lines.append(f"```sql\n{sql.strip()}\n```")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info('{name}')")
            cols = cursor.fetchall()
            if cols:
                schema_lines.append("**Columns:**")
                col_descs = [f"- `{c[1]}` ({c[2]}){' [PK]' if c[5] else ''}" for c in cols]
                schema_lines.extend(col_descs)
            schema_lines.append("")
            
        conn.close()
        return "\n".join(schema_lines)
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"


def get_sales_kpi_summary(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Calculate and return key e-commerce sales and advertising metrics."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Sales totals
        cursor.execute("SELECT SUM(total_sales), SUM(total_units_ordered), MIN(date), MAX(date) FROM daily_sales")
        sales_row = cursor.fetchone()
        total_sales = sales_row[0] or 0.0
        total_units = sales_row[1] or 0
        min_date = sales_row[2] or "N/A"
        max_date = sales_row[3] or "N/A"

        # Ad totals
        cursor.execute("SELECT SUM(ad_sales), SUM(ad_spend), SUM(clicks), SUM(impressions) FROM daily_ad_performance")
        ad_row = cursor.fetchone()
        ad_sales = ad_row[0] or 0.0
        ad_spend = ad_row[1] or 0.0
        clicks = ad_row[2] or 0
        impressions = ad_row[3] or 0

        # Product count
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN is_currently_eligible = 1 THEN 1 ELSE 0 END) FROM products")
        prod_row = cursor.fetchone()
        total_products = prod_row[0] or 0
        eligible_products = prod_row[1] or 0

        conn.close()

        roas = (ad_sales / ad_spend) if ad_spend > 0 else 0.0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        cpc = (ad_spend / clicks) if clicks > 0 else 0.0

        return {
            "total_sales_usd": round(total_sales, 2),
            "total_units_ordered": total_units,
            "total_ad_sales_usd": round(ad_sales, 2),
            "total_ad_spend_usd": round(ad_spend, 2),
            "blended_roas": round(roas, 2),
            "avg_cpc_usd": round(cpc, 2),
            "overall_ctr_pct": round(ctr, 2),
            "total_products": total_products,
            "eligible_products_for_ads": eligible_products,
            "date_range": f"{min_date} to {max_date}",
        }
    except Exception as e:
        return {"error": f"Error computing summary: {str(e)}"}


# LangChain tool wrappers
@tool
def execute_sql(query: str) -> str:
    """Execute a safe, read-only SQL query against the SQLite database and return results.
    
    Args:
        query: Valid SQLite SELECT statement.
    """
    res = execute_sql_query(query)
    if not res["success"]:
        return f"SQL Error: {res['error']}"
    
    rows = res["rows"]
    if not rows:
        return "Query succeeded but returned 0 rows."
    
    # Return formatted JSON string of rows (capped to first 25 for prompt efficiency)
    sample_rows = rows[:25]
    summary_str = f"Returned {res['row_count']} rows. First {len(sample_rows)} rows:\n{sample_rows}"
    return summary_str


@tool
def get_schema() -> str:
    """Retrieve the database schema, including all tables, views, and column definitions."""
    return get_database_schema()


@tool
def get_sales_summary() -> str:
    """Get high-level business KPI summary including total sales, ad spend, ROAS, and product counts."""
    summary = get_sales_kpi_summary()
    return str(summary)
