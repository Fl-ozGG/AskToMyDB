from fastapi import FastAPI
from pydantic import BaseModel
from ai_agent import ask_to_agent

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    

@app.post("/query")
def query_endpoint(request: QueryRequest):
    response = ask_to_agent(request.query)
    return {"data": response}