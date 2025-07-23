from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.agent import EcommerceAIAgent
import pandas as pd

app = FastAPI(title="E-commerce AI Agent API", version="1.0.0")
agent = EcommerceAIAgent()

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    question: str
    answer: str
    sql_query: str
    results: dict
    row_count: int

@app.get("/")
async def root():
    return {"message": "E-commerce AI Agent API", "status": "running"}

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        result = agent.query_database(request.question)
        
        if result.get('error'):
            raise HTTPException(status_code=400, detail=result['error'])
        
        results_dict = {}
        if result.get('results') is not None and not result['results'].empty:
            results_dict = result['results'].to_dict('records')
        
        return AnswerResponse(
            question=result['question'],
            answer=result.get('answer', 'Query executed successfully'),
            sql_query=result['sql'],
            results={"data": results_dict},
            row_count=result['row_count']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
