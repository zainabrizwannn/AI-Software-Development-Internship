from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import os
import json

from rag import (
    load_documents,
    retrieve,
    build_prompt
)

# Load Environment Variables
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# FastAPI App
app = FastAPI(title="Library AI Service")

# Load RAG documents once when the app starts
load_documents()

# Request / Response Models
class BookRequest(BaseModel):
    title: str
    description: str
class AskRequest(BaseModel):
    question: str
class AskResponse(BaseModel):
    answer: str
    sources: list[str]

# Home Endpoint
@app.get("/")
def home():
    return {
        "message": "AI Service Running"}

# Summarize Endpoint
@app.post("/summarize")
def summarize(book: BookRequest):
    prompt = f"""
You are a librarian and book expert.
Analyze the following book.

Title:
{book.title}
Description:
{book.description}
Return ONLY valid JSON in this exact format:
{{
    "genre": "Genre name",
    "summary": "A concise one-paragraph summary."}}
Do not include markdown.
Do not include explanation.
Do not wrap the JSON inside ``` blocks.
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt)
        text = response.text.strip()
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()
        result = json.loads(text)

        return result
    except json.JSONDecodeError:
        return {
            "error": "Unable to parse AI response."}
    except Exception as e:
        return {
            "error": str(e)}

# Ask Endpoint (RAG)
@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        chunks, metadatas = retrieve(req.question)
        if not chunks:
            return AskResponse(
                answer="I don't have that information.",
                sources=[])
        prompt = build_prompt(
            req.question,
            chunks)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt)
        sources = sorted(
            list(
                set(
                    meta["source"]
                    for meta in metadatas)))

        return AskResponse(
            answer=response.text,
            sources=sources)

    except Exception as e:
        return AskResponse(
            answer=f"Error: {str(e)}",
            sources=[])