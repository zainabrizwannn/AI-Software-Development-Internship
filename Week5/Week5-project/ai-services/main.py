import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

from rag import retrieve

load_dotenv()

app = FastAPI()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class QuestionRequest(BaseModel):
    question: str


class SummarizeRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {"message": "Library Knowledge Assistant API is running!"}


@app.post("/summarize")
def summarize(request: SummarizeRequest):

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"Summarize the following text:\n\n{request.text}"
    )

    return {
        "summary": response.text
    }


@app.post("/ask")
def ask(request: QuestionRequest):

    documents, metadata = retrieve(request.question)

    context = "\n\n".join(documents)

    prompt = f"""
You are a helpful AI library assistant.

Answer ONLY using the information below.

If the answer is not contained in the context, reply exactly:

I don't have that information.

Context:
{context}

Question:
{request.question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    sources = []

    for item in metadata:
        source = item.get("source")

        if source and source not in sources:
            sources.append(source)

    return {
        "answer": response.text,
        "sources": sources
    }