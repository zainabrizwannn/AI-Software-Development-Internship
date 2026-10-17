import asyncio
import json
import os
import sys

from pathlib import Path

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Request,
)
from fastapi.responses import (
    StreamingResponse,
)
from pydantic import BaseModel


# =========================================================
# IMPORT FINAL LANGGRAPH AGENT
# =========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

AGENT_DIR = (
    BASE_DIR
    / "agent"
)

if str(
    AGENT_DIR
) not in sys.path:
    sys.path.insert(
        0,
        str(
            AGENT_DIR
        ),
    )


from hitl_workflow import (
    checkpoint_contains_token,
    resume_persistent_run,
    start_persistent_run,
)


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
            "AGENT_SERVICE_KEY "
            "is not configured."
        )

    if (
        x_service_key
        != expected
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid service key.",
        )


def extract_bearer_token(
    authorization: str | None,
) -> str:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail=(
                "Missing forwarded "
                "user authorization."
            ),
        )

    prefix = "Bearer "

    if not authorization.startswith(
        prefix
    ):
        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid authorization "
                "header."
            ),
        )

    token = authorization[
        len(prefix):
    ].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing bearer token.",
        )

    return token


# =========================================================
# SSE
# =========================================================

def sse_event(
    event_name: str,
    payload: dict,
) -> str:

    return (
        f"event: {event_name}\n"
        f"data: "
        f"{json.dumps(payload)}"
        f"\n\n"
    )


# =========================================================
# RESULT HELPERS
# =========================================================

def interrupt_payload(
    result: dict,
) -> dict | None:

    interrupts = result.get(
        "__interrupt__"
    )

    if not interrupts:
        return None

    first = interrupts[0]

    value = getattr(
        first,
        "value",
        first,
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    return None


def final_answer(
    result: dict,
) -> str:

    answer = result.get(
        "final_answer"
    )

    if answer:
        return str(
            answer
        )

    messages = result.get(
        "messages",
        [],
    )

    if messages:
        last = messages[-1]

        content = getattr(
            last,
            "content",
            "",
        )

        if content:
            return str(
                content
            )

    tool_result = result.get(
        "tool_result",
        ""
    )

    if tool_result:
        return str(
            tool_result
        )

    return (
        "The agent completed the request."
    )


# =========================================================
# START
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

    user_token = (
        extract_bearer_token(
            authorization
        )
    )

    async def stream():

        try:

            yield sse_event(
                "step",
                {
                    "kind":
                        "tool_call",

                    "name":
                        "agent_router",

                    "summary":
                        (
                            "Routing the request "
                            "through the LangGraph "
                            "workflow."
                        ),
                },
            )

            if await request.is_disconnected():
                return


            result = await asyncio.to_thread(
                start_persistent_run,
                body.thread_id,
                body.message,
                user_token,
            )


            if await request.is_disconnected():
                return


            # -----------------------------------------
            # SECURITY ASSERTION
            # -----------------------------------------

            token_leaked = (
                checkpoint_contains_token(
                    user_token
                )
            )

            if token_leaked:
                yield sse_event(
                    "error",
                    {
                        "code":
                            "CHECKPOINT_SECRET_LEAK",

                        "message":
                            (
                                "A runtime credential "
                                "was detected in the "
                                "checkpoint file."
                            ),

                        "retryable":
                            False,
                    },
                )

                return


            # -----------------------------------------
            # APPROVAL INTERRUPT
            # -----------------------------------------

            pending = interrupt_payload(
                result
            )

            if pending:

                calls = pending.get(
                    "calls",
                    [],
                )

                yield sse_event(
                    "step",
                    {
                        "kind":
                            "tool_result",

                        "name":
                            "check_availability",

                        "summary":
                            (
                                "The selected book was "
                                "checked. Approval is "
                                "required before the "
                                "reservation write."
                            ),
                    },
                )

                yield sse_event(
                    "approval_required",
                    {
                        "threadId":
                            body.thread_id,

                        "calls":
                            calls,
                    },
                )

                return


            # -----------------------------------------
            # NORMAL COMPLETION
            # -----------------------------------------

            tool_result = result.get(
                "tool_result",
                "",
            )

            if tool_result:

                yield sse_event(
                    "step",
                    {
                        "kind":
                            "tool_result",

                        "name":
                            "agent_tool",

                        "summary":
                            str(
                                tool_result
                            ),
                    },
                )


            answer = final_answer(
                result
            )

            # Send final answer as token fragments
            # so the Angular timeline still supports
            # streaming text.
            for word in answer.split():

                if (
                    await request
                    .is_disconnected()
                ):
                    return

                yield sse_event(
                    "token",
                    {
                        "text":
                            word + " "
                    },
                )

                await asyncio.sleep(
                    0.02
                )


            yield sse_event(
                "final",
                {
                    "answer":
                        answer,

                    "sources": [
                        "library catalog",
                        "LangGraph workflow",
                    ],
                },
            )


        except Exception as exc:

            yield sse_event(
                "error",
                {
                    "code":
                        "AGENT_RUN_FAILED",

                    "message":
                        str(
                            exc
                        ),

                    "retryable":
                        True,
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
# RESUME
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

    user_token = (
        extract_bearer_token(
            authorization
        )
    )


    # Guard against mismatched body/path thread IDs.
    if (
        body.thread_id
        != thread_id
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Thread ID in request body "
                "does not match route."
            ),
        )


    async def stream():

        try:

            if body.approved:

                yield sse_event(
                    "step",
                    {
                        "kind":
                            "tool_call",

                        "name":
                            "reserve_book",

                        "summary":
                            (
                                "Approval received. "
                                "Executing the secure "
                                "reservation tool."
                            ),
                    },
                )

            else:

                yield sse_event(
                    "step",
                    {
                        "kind":
                            "tool_result",

                        "name":
                            "approval",

                        "summary":
                            (
                                "The user rejected "
                                "the reservation."
                            ),
                    },
                )


            if await request.is_disconnected():
                return


            result = await asyncio.to_thread(
                resume_persistent_run,
                thread_id,
                body.approved,
                user_token,
            )


            if await request.is_disconnected():
                return


            token_leaked = (
                checkpoint_contains_token(
                    user_token
                )
            )

            if token_leaked:

                yield sse_event(
                    "error",
                    {
                        "code":
                            "CHECKPOINT_SECRET_LEAK",

                        "message":
                            (
                                "A runtime credential "
                                "was detected in the "
                                "checkpoint file."
                            ),

                        "retryable":
                            False,
                    },
                )

                return


            tool_result = result.get(
                "tool_result",
                "",
            )

            if (
                body.approved
                and tool_result
            ):

                yield sse_event(
                    "step",
                    {
                        "kind":
                            "tool_result",

                        "name":
                            "reserve_book",

                        "summary":
                            str(
                                tool_result
                            ),
                    },
                )


            answer = final_answer(
                result
            )


            # Conflict/re-plan is visible explicitly.
            if (
                "re-plan"
                in answer.lower()
                or
                "no longer available"
                in answer.lower()
            ):

                yield sse_event(
                    "step",
                    {
                        "kind":
                            "tool_result",

                        "name":
                            "replan",

                        "summary":
                            (
                                "Reservation conflict "
                                "detected. The agent "
                                "searched for another "
                                "catalog option instead "
                                "of looping."
                            ),
                    },
                )


            yield sse_event(
                "final",
                {
                    "answer":
                        answer,

                    "sources": [
                        "library catalog",
                        "reservation service",
                    ],
                },
            )


        except Exception as exc:

            yield sse_event(
                "error",
                {
                    "code":
                        "AGENT_RESUME_FAILED",

                    "message":
                        str(
                            exc
                        ),

                    "retryable":
                        True,
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