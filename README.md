# E-commerce AI Analytics — Agentic Data Analyst

An AI-powered e-commerce analytics assistant that allows users to query business data using natural language. Built with **LangChain** and **LangGraph**, the system plans and validates SQL, utilizes safe tools to analyze SQLite data, automatically creates visualizations when useful, features an automatic SQL self-correction retry loop, and exposes analytics capabilities through the **Model Context Protocol (MCP)**.

---

## 🎯 Project Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                    E-COMMERCE AGENTIC AI ANALYTICS                           │
│              Autonomous Natural Language → SQL → Insight Pipeline            │
├──────────────────────────────────────────────────────────────────────────────┤
│ 📊 FACTUAL DATASET METRICS              ✨ CORE CAPABILITIES                 │
│ • 4,600+ Database Records               • LangGraph Workflow Orchestration   │
│ • 270 Active Product SKUs               • Safe Read-Only SQL Tool Execution  │
│ • $1,000,000+ Total Sales Tracked       • Automated SQL Error Retry Loop     │
│ • 14 Days High-Granularity Ad Spend     • Adaptive Dark-Themed Visualizations│
│ • Multi-Provider: Gemini & Groq         • Standard Model Context Protocol    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ System Architecture

```text
                           User Question
                                 ↓
                    Streamlit UI / FastAPI REST
                                 ↓
                  LangGraph Agent (StateGraph)
                                 ↓
                      [ analyze_and_plan ]
              (LLM Structured Output: QueryPlan)
                                 ↓
                      [ execute_query ]
               (Tool 1: Read-Only SQLite Exec)
                                 │
                   ┌─────────────┴─────────────┐
                   │ Query Succeeded?          │
                   ▼                           ▼
                 [ YES ]                     [ NO ]
                   │                           │ (Retry < 2)
                   │                           ▼
                   │                    [ correct_sql ]
                   │                  (Self-Correction)
                   │                           │
                   │                           └────────┐
                   │                                    │
                   ▼                                    ▼
         [ synthesize_insight ] ◄───────────────────────┘
      (Natural Language Answer +
       Business Analyst Insight)
                   │
                   ▼
       Visualization Decision
    (Bar Chart / Line Chart / Pie)
                   │
                   ▼
     Final Response Card to User
```

---

## ✨ Features

- **Natural Language Analytics**: Query complex e-commerce sales, product performance, and advertising data without writing SQL.
- **LangGraph Orchestration**: Robust state graph with explicit nodes, conditional routing, error states, and execution step logging.
- **Structured Outputs**: Uses Pydantic schemas (`QueryPlan`, `SQLCorrection`, `AgentInsight`) to enforce deterministic decisions from LLMs.
- **SQL Validation & Retry Loop**: Pre-execution security checks ensure queries are read-only (`SELECT`/`WITH` only). Runtime SQLite errors trigger an automatic model correction loop before returning results.
- **Model Context Protocol (MCP)**: Exposes analytics tools (`execute_sql`, `get_schema`, `get_sales_summary`) via an MCP server compatible with Antigravity, Claude Desktop, Cursor, and other MCP clients.
- **Automated Visualizations**: Determines whether a question benefits from a visual chart (Rankings → Bar, Trends → Line, Proportions → Pie, Scalars → Clean Value Card).
- **Dual Interface**: Includes an interactive **Streamlit** dashboard and a **FastAPI** REST API.
- **Multi-Model Provider Support**: Seamlessly works with Google Gemini (`gemini-2.5-flash`) or Groq (`llama-3.1-8b-instant`), with rule-based fallback if no key is supplied.

---

## 📂 Project Structure

```text
ecommerce-ai-analytics/
├── core/
│   ├── agent.py          # EcommerceAIAgent wrapper & public interface
│   ├── graph.py          # LangGraph StateGraph, nodes, and planning logic
│   ├── tools.py          # Read-only SQLite query, schema, and KPI tools
│   └── prompts.py        # System instructions for planning, retry, and insight
├── mcp/
│   └── server.py         # FastMCP analytical server (stdio / JSON-RPC)
├── ui/
│   └── components.py     # Streamlit cards, metrics sidebar, and result display
├── utils/
│   ├── explanations.py   # Statistical summaries and formatted metrics
│   └── visualization.py  # Adaptive dark-theme Matplotlib/Seaborn charts
├── data/
│   ├── processor.py      # ETL pipeline loading CSVs into SQLite
│   ├── total_sales.csv   # Daily sales records
│   ├── ad_sales.csv      # Daily advertising metrics (ROAS, CPC, CTR)
│   └── eligibility.csv   # Product ad eligibility logs
├── app.py                # Streamlit web application
├── api.py                # FastAPI REST service
├── ecommerce_optimized.db# SQLite analytical database (4,600+ records)
├── requirements.txt      # Project dependencies
├── .env.example          # Environment variable template
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/katta-karthik/ai_agent_for_ecommerce-data.git
cd ai_agent_for_ecommerce-data

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Add your preferred API key (Gemini recommended, or Groq):

```ini
GOOGLE_API_KEY=your_gemini_api_key_here
# or
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Streamlit Application

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### 4. (Optional) Run the FastAPI REST Server

```bash
python api.py
```

Test the API via cURL or Postman:

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is my total sales?"}'
```

---

## 🔍 Example Questions

### 📈 Basic & KPIs
- *"What is my total sales?"*
- *"What is the average Return on Ad Spend (ROAS)?"*
- *"How many products do I have in the catalog?"*

### 🏆 Rankings & Comparisons
- *"Which products generated the highest revenue?"*
- *"Show me the top 10 products by total sales."*
- *"What are the best performing products by ROAS?"*

### 📅 Trends Over Time
- *"Show monthly sales trend."*
- *"What was the daily sales breakdown over the recorded period?"*
- *"Compare advertising spend versus advertising sales."*

---

## 🔌 Model Context Protocol (MCP) Server

To expose the analytics capabilities to MCP-enabled tools (e.g., Claude Code, Cursor, Antigravity, Claude Desktop):

```bash
python mcp/server.py
```

**Exposed Tools:**
- `execute_sql(query)`: Executes a safe, read-only SELECT query against the SQLite database.
- `get_schema()`: Returns all table definitions, column types, and views.
- `get_sales_summary()`: Returns high-level store KPIs (Revenue, ROAS, CPC, CTR).

---

## 🛡️ Database & Security

- **Strict Read-Only Enforcement**: Query sanitization rejects non-SELECT operations (`DROP`, `DELETE`, `UPDATE`, `ALTER`, etc.).
- **Optimized SQLite Schema**: Indexed on `date`, `item_id`, `roas`, and `cpc` for sub-millisecond local query performance.
- **Graceful Error Handling**: Database syntax errors trigger the LangGraph self-correction loop without crashing the UI.
