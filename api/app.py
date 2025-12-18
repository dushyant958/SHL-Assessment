from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from retrieval_engine import RetrievalEngine
import uvicorn

app = FastAPI(title="SHL Assessment Recommendation API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine
engine = RetrievalEngine()

class QueryRequest(BaseModel):
    query: str

class RecommendationResponse(BaseModel):
    assessment_name: str
    assessment_url: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/recommend", response_model=list[RecommendationResponse])
def recommend(request: QueryRequest):
    try:
        results = engine.retrieve(request.query, top_k=10)
        
        # Format response per SHL spec
        recommendations = [
            {
                "assessment_name": rec["assessment_name"],
                "assessment_url": rec["assessment_url"]
            }
            for rec in results
        ]
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)