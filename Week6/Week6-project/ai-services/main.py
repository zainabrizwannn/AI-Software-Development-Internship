import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai

from rag import (
    ask_structured,
    ask_text,
    stream_answer,
    clear_session
)


load_dotenv()

app = FastAPI(
    title="Library AI Assistant",
    version="0.6"
)


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class QuestionRequest(BaseModel):
    question: str
    session_id: str = "default-session"


class SummarizeRequest(BaseModel):
    text: str


class ClearSessionRequest(BaseModel):
    session_id: str


@app.get("/")
def home():
    return {
        "message": (
            "Library Knowledge Assistant "
            "API is running!"
        )
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "library-ai-assistant"
    }


@app.post("/summarize")
def summarize(
    request: SummarizeRequest
):

    response = (
        client.models.generate_content(
            model="gemini-3.6-flash",
            contents=(
                "Summarize the following "
                "text:\n\n"
                f"{request.text}"
            )
        )
    )

    return {
        "summary": response.text
    }


@app.post("/ask")
def ask(
    request: QuestionRequest
):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question is required."
        )

    try:

        result = ask_structured(
            question=request.question,
            session_id=request.session_id
        )

        parsed = result.get(
            "parsed"
        )

        if parsed is not None:

            return {
                "answer": parsed.answer,
                "confidence": (
                    parsed.confidence
                ),
                "sources": parsed.sources,
                "session_id": (
                    request.session_id
                )
            }

        raw = result.get(
            "raw"
        )

        raw_text = ""

        if raw is not None:
            raw_text = (
                raw.content
                if hasattr(
                    raw,
                    "content"
                )
                else str(raw)
            )

        return {
            "answer": raw_text,
            "confidence": "unknown",
            "sources": [],
            "session_id": (
                request.session_id
            )
        }

    except Exception as error:

        print(
            "Ask endpoint error:",
            str(error)
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "The AI assistant is "
                "temporarily unavailable."
            )
        )


@app.post("/ask/text")
def ask_text_endpoint(
    request: QuestionRequest
):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question is required."
        )

    try:

        answer = ask_text(
            question=request.question,
            session_id=request.session_id
        )

        return {
            "answer": answer,
            "session_id": (
                request.session_id
            )
        }

    except Exception as error:

        print(
            "Text endpoint error:",
            str(error)
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "The AI assistant is "
                "temporarily unavailable."
            )
        )


@app.post("/ask/stream")
def ask_stream(
    request: QuestionRequest
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question is required."
        )

    def event_generator():

        try:

            for text in stream_answer(
                question=request.question,
                session_id=request.session_id
            ):

                if not text:
                    continue

                safe_text = str(
                    text
                ).replace(
                    "\r",
                    ""
                )

                lines = (
                    safe_text.split(
                        "\n"
                    )
                )

                for line in lines:
                    yield (
                        f"data: {line}\n"
                    )

                yield "\n"

        except Exception as error:

            print(
                "Streaming error:",
                repr(error)
            )

            yield (
                "data: The AI assistant is temporarily unavailable.\n\n"
            )

        finally:

            yield (
                "data: [DONE]\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":
                "no-cache",
            "Connection":
                "keep-alive",
            "X-Accel-Buffering":
                "no"
        }
    )

    def event_generator():

        try:

            for text in stream_answer(
                question=request.question,
                session_id=(
                    request.session_id
                )
            ):

                if not text:
                    continue

                yield (
                    f"data: {text}\n\n"
                )

        except Exception as error:

            print(
                "Streaming error:",
                str(error)
            )

            yield (
                "data: The AI assistant "
                "is temporarily unavailable."
                "\n\n"
            )

        finally:

            yield (
                "data: [DONE]\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@app.post("/session/clear")
def clear_chat_session(
    request: ClearSessionRequest
):

    clear_session(
        request.session_id
    )

    return {
        "message": (
            "Session memory cleared."
        ),
        "session_id": (
            request.session_id
        )
    }