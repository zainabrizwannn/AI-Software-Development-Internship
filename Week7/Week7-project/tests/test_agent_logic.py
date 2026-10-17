import sys
from pathlib import Path

import httpx
import pytest
import respx

from httpx import Response
from pydantic import ValidationError


# =========================================================
# FINAL WEEK 7 PROJECT PATH
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

AGENT_DIR = (
    PROJECT_ROOT
    / "ai-services"
    / "agent"
)

sys.path.insert(
    0,
    str(AGENT_DIR),
)


# =========================================================
# IMPORT FINAL PROJECT CODE
# =========================================================

from secure_tools import reserve_book
from retry_workflow import after_tools


DOTNET_URL = "http://localhost:5194"


# =========================================================
# RETRY / REPLAN LOGIC
# =========================================================

def test_after_tools_final_error_triggers_stop():

    state = {
        "messages": [],
        "retries": 0,
        "plan": "",
        "tool_result":
            "ERROR_FINAL: already reserved",
    }

    assert after_tools(state) == "stop"


def test_after_tools_conflict_triggers_replan():

    state = {
        "messages": [],
        "retries": 0,
        "plan": "",
        "tool_result":
            "ERROR_CONFLICT: already reserved",
    }

    assert after_tools(state) == "replan"


def test_after_tools_retryable_error_triggers_retry():

    state = {
        "messages": [],
        "retries": 0,
        "plan": "",
        "tool_result":
            "ERROR_RETRYABLE: temporary failure",
    }

    assert after_tools(state) == "retry"


def test_after_tools_success_goes_to_success():

    state = {
        "messages": [],
        "retries": 0,
        "plan": "",
        "tool_result":
            "OK: reservation created",
    }

    assert after_tools(state) == "success"


# =========================================================
# PYDANTIC ARGUMENT VALIDATION
# =========================================================

def test_reserve_rejects_negative_id():

    with pytest.raises(
        ValidationError
    ):
        reserve_book.invoke(
            {
                "book_id": -1
            },
            config={
                "configurable": {
                    "user_token":
                        "test-token"
                }
            },
        )


def test_reserve_rejects_zero_id():

    with pytest.raises(
        ValidationError
    ):
        reserve_book.invoke(
            {
                "book_id": 0
            },
            config={
                "configurable": {
                    "user_token":
                        "test-token"
                }
            },
        )


# =========================================================
# HTTP STATUS MAPPING
# =========================================================

@respx.mock
def test_reserve_maps_409_to_final_error():

    respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        return_value=Response(
            409,
            json={
                "message":
                    "Already reserved"
            },
        )
    )

    result = reserve_book.invoke(
        {
            "book_id": 4
        },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "pytest-409",
            }
        },
    )

    assert result.startswith(
        "ERROR_FINAL"
    )


@respx.mock
def test_reserve_maps_404_to_final_error():

    respx.post(
        f"{DOTNET_URL}/api/Books/999999/reserve"
    ).mock(
        return_value=Response(
            404,
            json={
                "message":
                    "Book not found"
            },
        )
    )

    result = reserve_book.invoke(
        {
            "book_id": 999999
        },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "pytest-404",
            }
        },
    )

    assert result.startswith(
        "ERROR_FINAL"
    )


@respx.mock
def test_reserve_maps_401_to_final_error():

    respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        return_value=Response(
            401
        )
    )

    result = reserve_book.invoke(
        {
            "book_id": 4
        },
        config={
            "configurable": {
                "user_token":
                    "bad-token",
                "idempotency_key":
                    "pytest-401",
            }
        },
    )

    assert result.startswith(
        "ERROR_FINAL"
    )


@respx.mock
def test_reserve_maps_403_to_final_error():

    respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        return_value=Response(
            403
        )
    )

    result = reserve_book.invoke(
        {
            "book_id": 4
        },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "pytest-403",
            }
        },
    )

    assert result.startswith(
        "ERROR_FINAL"
    )


@respx.mock
def test_reserve_maps_400_to_final_error():

    respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        return_value=Response(
            400,
            json={
                "message":
                    "Bad request"
            },
        )
    )

    result = reserve_book.invoke(
        {
            "book_id": 4
        },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "pytest-400",
            }
        },
    )

    assert result.startswith(
        "ERROR_FINAL"
    )


# =========================================================
# NETWORK FAILURE MAPPING
# =========================================================

@respx.mock
def test_reserve_connection_error_is_retryable():

    respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        side_effect=httpx.ConnectError(
            "Connection failed"
        )
    )

    result = reserve_book.invoke(
        {
            "book_id": 4
        },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "pytest-connect",
            }
        },
    )

    assert result.startswith(
        "ERROR_RETRYABLE"
    )


@respx.mock
def test_reserve_timeout_is_retryable():

    respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        side_effect=httpx.ReadTimeout(
            "Request timed out"
        )
    )

    result = reserve_book.invoke(
        {
            "book_id": 4
        },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "pytest-timeout",
            }
        },
    )

    assert result.startswith(
        "ERROR_RETRYABLE"
    )


# =========================================================
# SUCCESS + SECURITY HEADERS
# =========================================================

@respx.mock
def test_reserve_success_returns_ok():

    respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        return_value=Response(
            200,
            json={
                "reservationId": 10,
                "bookId": 4,
                "title": "Test Book",
                "userId": "1002",
            },
        )
    )

    result = reserve_book.invoke(
        {
            "book_id": 4
        },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "pytest-success",
            }
        },
    )

    assert result.startswith(
        "OK"
    )


@respx.mock
def test_reserve_sends_authorization_header():

    route = respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        return_value=Response(
            200,
            json={
                "reservationId": 11,
                "bookId": 4,
                "title": "Test Book",
                "userId": "1002",
            },
        )
    )

    reserve_book.invoke(
        {
            "book_id": 4
        },
        config={
            "configurable": {
                "user_token":
                    "jwt-test-token",
                "idempotency_key":
                    "pytest-auth",
            }
        },
    )

    assert route.called

    request = route.calls[0].request

    assert (
        request.headers[
            "Authorization"
        ]
        ==
        "Bearer jwt-test-token"
    )


@respx.mock
def test_reserve_sends_idempotency_key():

    route = respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        return_value=Response(
            200,
            json={
                "reservationId": 12,
                "bookId": 4,
                "title": "Test Book",
                "userId": "1002",
            },
        )
    )

    reserve_book.invoke(
        {
            "book_id": 4
        },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "fixed-key",
            }
        },
    )

    assert route.called

    request = route.calls[0].request

    assert (
        "Idempotency-Key"
        in request.headers
    )