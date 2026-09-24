"""E-commerce Analytics Model Context Protocol (MCP) Server.

Exposes read-only SQLite database analytical tools to any MCP-compatible client
(e.g., Claude Desktop, Claude Code, Cursor, Antigravity, or LangChain agents).
"""

import sys
import os

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcp.server.mcpserver import MCPServer
from core.tools import execute_sql_query, get_database_schema, get_sales_kpi_summary, DEFAULT_DB_PATH

# Initialize MCP Server
server = MCPServer("ecommerce-analytics-server")


@server.tool()
def execute_sql(query: str) -> str:
    """Execute a safe, read-only SQL query against the e-commerce SQLite database.
    
    Only SELECT or CTE queries are permitted. Destructive statements (DROP, DELETE, UPDATE)
    are strictly rejected.

    Args:
        query: Valid SQLite SELECT statement.
    """
    res = execute_sql_query(query, db_path=os.path.join(PROJECT_ROOT, DEFAULT_DB_PATH))
    if not res["success"]:
        return f"SQL Error: {res['error']}"
    
    rows = res["rows"]
    if not rows:
        return "Query succeeded with 0 rows returned."
    
    return f"Returned {res['row_count']} rows:\n{rows[:25]}"


@server.tool()
def get_schema() -> str:
    """Retrieve the e-commerce database schema, including tables, views, and columns."""
    return get_database_schema(db_path=os.path.join(PROJECT_ROOT, DEFAULT_DB_PATH))


@server.tool()
def get_sales_summary() -> str:
    """Get high-level business KPI summary including total revenue, ad spend, ROAS, and product counts."""
    summary = get_sales_kpi_summary(db_path=os.path.join(PROJECT_ROOT, DEFAULT_DB_PATH))
    return str(summary)


if __name__ == "__main__":
    # Runs the MCP server over stdio transport
    server.run()
