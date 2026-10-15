import asyncio
import json
import os

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Request,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


# =========================================================
# REQUEST MODELS
# =========================================================

class AgentRunRequest(BaseModel):
    thread_id: str
    message: str


class ResumeRequest(BaseModel):
    thread_id: str
    approved: bool


# =========================================================
# SECURITY
# =========================================================

def verify_service_key(
    x_service_key: str | None,
):
    expected = os.getenv(
        "AGENT_SERVICE_KEY"
    )

    if not expected:
        raise RuntimeError(
            "AGENT_SERVICE_KEY is not configured."
        )

    if x_service_key != expected:
        raise HTTPException(
            status_code=401,
            detail="Invalid service key.",
        )


# =========================================================
# SSE HELPERS
# =========================================================

def sse_event(
    event_name: str,
    payload: dict,
) -> str:

    return (
        f"event: {event_name}\n"
        f"data: {json.dumps(payload)}\n\n"
    )


# =========================================================
# START AGENT RUN
# =========================================================

@router.post("/runs")
async def start_agent_run(
    body: AgentRunRequest,
    request: Request,
    x_service_key: str | None = Header(
        default=None,
        alias="X-Service-Key",
    ),
    authorization: str | None = Header(
        default=None,
        alias="Authorization",
    ),
):
    verify_service_key(
        x_service_key
    )

    # IMPORTANT:
    # The forwarded user JWT is available only
    # during this request. It is NOT stored.

    async def stream():

        yield sse_event(
            "step",
            {
                "kind": "tool_call",
                "name": "search_catalog",
                "summary": (
                    "Searching the library catalog."
                ),
            },
        )

        await asyncio.sleep(0.4)

        if await request.is_disconnected():
            print(
                f"Client disconnected: "
                f"{body.thread_id}"
            )
            return

        yield sse_event(
            "step",
            {
                "kind": "tool_result",
                "name": "search_catalog",
                "summary": (
                    "Found an available "
                    "science-fiction book."
                ),
            },
        )

        await asyncio.sleep(0.4)

        lower = (
            body.message.lower()
        )

        # ---------------------------------------------
        # WRITE ACTION -> APPROVAL
        # ---------------------------------------------

        if (
            "reserve" in lower
            or "book it" in lower
        ):
            yield sse_event(
                "approval_required",
                {
                    "threadId":
                        body.thread_id,

                    "calls":
                        [
                            {
                                "name":
                                    "reserve_book",

                                "args":
                                    {
                                        "book_id": 1
                                    },
                            }
                        ],
                },
            )

            print(
                f"Run paused for approval: "
                f"{body.thread_id}"
            )

            return

        # ---------------------------------------------
        # READ-ONLY ANSWER
        # ---------------------------------------------

        text = (
            "I found Dune and it is "
            "currently available."
        )

        for word in (
            text.split()
        ):
            if await request.is_disconnected():
                print(
                    f"Generation cancelled: "
                    f"{body.thread_id}"
                )
                return

            yield sse_event(
                "token",
                {
                    "text":
                        word + " "
                },
            )

            await asyncio.sleep(
                0.08
            )

        yield sse_event(
            "final",
            {
                "answer": text,
                "sources": [
                    "library catalog"
                ],
            },
        )

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":
                "no-cache",
            "Connection":
                "keep-alive",
        },
    )


# =========================================================
# RESUME AFTER APPROVAL
# =========================================================

@router.post(
    "/runs/{thread_id}/resume"
)
async def resume_agent_run(
    thread_id: str,
    body: ResumeRequest,
    request: Request,
    x_service_key: str | None = Header(
        default=None,
        alias="X-Service-Key",
    ),
    authorization: str | None = Header(
        default=None,
        alias="Authorization",
    ),
):
    verify_service_key(
        x_service_key
    )

    async def stream():

        if not body.approved:

            yield sse_event(
                "final",
                {
                    "answer":
                        "The reservation was rejected.",

                    "sources":
                        [],
                },
            )

            return

        yield sse_event(
            "step",
            {
                "kind":
                    "tool_call",

                "name":
                    "reserve_book",

                "summary":
                    "Creating the reservation.",
            },
        )

        await asyncio.sleep(
            0.4
        )

        if await request.is_disconnected():
            print(
                f"Resume cancelled: "
                f"{thread_id}"
            )
            return

        yield sse_event(
            "step",
            {
                "kind":
                    "tool_result",

                "name":
                    "reserve_book",

                "summary":
                    "Reservation created.",
            },
        )

        yield sse_event(
            "final",
            {
                "answer":
                    "Dune was reserved successfully.",

                "sources":
                    [],
            },
        )

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
    )