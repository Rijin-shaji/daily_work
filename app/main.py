from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    user_type: str
    query: str

@app.get("/")
def home():
    return {"message": "AI Recruitment API Running"}

@app.post("/llm/query")
def query_llm(request: QueryRequest):

    query = request.query

    # Step 1: search resumes
    results = search_resumes(query)

    # Step 2: rank results
    ranked_results = rank_candidates(results)

    return {
        "query": query,
        "results": ranked_results
    }