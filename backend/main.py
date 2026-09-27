from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import run_proponent, run_antagonist

app = FastAPI(title="Tribunal API")

# Allow the Next.js frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later, fine for local dev
    allow_methods=["*"],
    allow_headers=["*"],
)


class DecisionRequest(BaseModel):
    question: str


@app.get("/")
def health_check():
    return {"status": "Tribunal backend is running"}


@app.post("/analyze/proponent")
def analyze_proponent(request: DecisionRequest):
    try:
        result = run_proponent(request.question)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/antagonist")
def analyze_antagonist(request: DecisionRequest):
    try:
        result = run_antagonist(request.question)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))