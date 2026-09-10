from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SummaryRequest(BaseModel):
    title: str
    description: str

class GenreRequest(BaseModel):
    title: str
    description: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/summarize")
def summarize(req: SummaryRequest):
    return {
        "title": req.title,
        "received": True
    }

@app.post("/genre-suggestion")
def genre_suggestion(req: GenreRequest):
    return {
        "title": req.title,
        "genre": "Self-Help"
    }