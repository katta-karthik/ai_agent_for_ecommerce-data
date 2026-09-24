"""FastAPI REST API for E-commerce AI Analytics Agent."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from core.agent import EcommerceAIAgent

app = FastAPI(
    title="E-commerce AI Agent API",
    version="2.0.0",
    description="Agentic Data Analytics API powered by LangGraph, LangChain, and SQLite."
)

agent = EcommerceAIAgent()


class QuestionRequest(BaseModel):
    question: str = Field(..., json_schema_extra={"example": "Which products generated the highest revenue?"})


class AnswerResponse(BaseModel):
    question: str
    answer: str
    business_insight: str
    recommendations: Optional[str] = None
    sql_query: str
    results: Dict[str, Any]
    row_count: int
    needs_visualization: bool = False
    visualization_type: Optional[str] = None
    steps: List[str] = []


@app.get("/")
async def root():
    return {
        "message": "E-commerce AI Agentic Analytics API",
        "version": "2.0.0",
        "orchestration": "LangGraph",
        "status": "online"
    }


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        result = agent.run(request.question)
        
        if result.get("error") and result.get("row_count") == 0 and not result.get("answer"):
            raise HTTPException(status_code=400, detail=result["error"])

        df = result.get("results")
        results_data = df.to_dict(orient="records") if (df is not None and not df.empty) else []

        return AnswerResponse(
            question=result["question"],
            answer=result["answer"],
            business_insight=result.get("business_insight", ""),
            recommendations=result.get("recommendations"),
            sql_query=result.get("sql", ""),
            results={"data": results_data},
            row_count=result.get("row_count", len(results_data)),
            needs_visualization=result.get("needs_visualization", False),
            visualization_type=result.get("visualization_type"),
            steps=result.get("steps", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schema")
async def get_schema():
    """Retrieve full database schema."""
    return {"schema": agent.get_schema()}


@app.get("/summary")
async def get_summary():
    """Retrieve key e-commerce sales and advertising KPIs."""
    return agent.get_summary()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "ready", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
