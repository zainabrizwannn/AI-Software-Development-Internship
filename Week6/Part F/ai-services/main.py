import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai

from rag import retrieve


load_dotenv()

app = FastAPI()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class QuestionRequest(BaseModel):
    question: str


class SummarizeRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {
        "message": "Library Knowledge Assistant API is running!"
    }


@app.post("/summarize")
def summarize(request: SummarizeRequest):

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=(
            "Summarize the following text:\n\n"
            f"{request.text}"
        )
    )

    return {
        "summary": response.text
    }


def build_rag_prompt(
    question: str,
    documents: list[str]
) -> str:

    context = "\n\n".join(documents)

    return f"""
You are a helpful AI library assistant.

Answer ONLY using the information below.

If the answer is not contained in the context, reply exactly:

I don't have that information.

Context:
{context}

Question:
{question}

Answer:
"""


@app.post("/ask")
def ask(request: QuestionRequest):

    documents, metadata = retrieve(
        request.question
    )

    prompt = build_rag_prompt(
        request.question,
        documents
    )

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


@app.post("/ask/stream")
def ask_stream(request: QuestionRequest):

    documents, metadata = retrieve(
        request.question
    )

    prompt = build_rag_prompt(
        request.question,
        documents
    )

    def event_generator():
        stream = client.models.generate_content_stream(
            model="gemini-3.6-flash",
            contents=prompt
        )

        for chunk in stream:
            text = chunk.text
            if not text:
                continue
            yield f"data: {text}\n\n"
            time.sleep(0.3)
        yield "data: [DONE]\n\n"
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )