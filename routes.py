from fastapi import FastAPI
from pydantic import BaseModel
from app import ask_to_llm

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
def query_endpoint(request: QueryRequest):
    response = ask_to_llm(request.query)
    return {"data": response}
