import sys
from pathlib import Path

import pytest
import respx
from httpx import Response
from pydantic import ValidationError


# ---------------------------------------------------------
# PATH SETUP
# ---------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]

PART_B = (
    REPO_ROOT
    / "Week7"
    / "Part B"
)

PART_C = (
    REPO_ROOT
    / "Week7"
    / "Part C"
)

sys.path.insert(
    0,
    str(PART_B),
)

sys.path.insert(
    0,
    str(PART_C),
)


# ---------------------------------------------------------
# IMPORT EXISTING WEEK 7 CODE
# ---------------------------------------------------------

from secure_tools import reserve_book
from retry_workflow import after_tools


DOTNET_URL = "http://localhost:5194"


# ---------------------------------------------------------
# TEST 1
# Final error should trigger replan
# ---------------------------------------------------------

def test_after_tools_final_error_triggers_stop():
    state = {
        "messages": [],
        "retries": 0,
        "plan": "",
        "tool_result":
            "ERROR_FINAL: already reserved",
    }
    result = after_tools(state)
    assert result == "stop"

def test_after_tools_conflict_triggers_replan():
    state = {
        "messages": [],
        "retries": 0,
        "plan": "",
        "tool_result":
            "ERROR_CONFLICT: already reserved",
    }
    result = after_tools(state)
    assert result == "replan"

# ---------------------------------------------------------
# TEST 2
# Retryable error should retry
def test_after_tools_retryable_error_triggers_retry():
    state = {
        "messages": [],
        "retries": 0,
        "plan": "",
        "tool_result":
            "ERROR_RETRYABLE: temporary network error",
    }
    result = after_tools(state)
    assert result == "retry"
# ---------------------------------------------------------
# TEST 3
# Successful result should finish
def test_after_tools_success_goes_to_success():
    state = {
        "messages": [],
        "retries": 0,
        "plan": "",
        "tool_result":
            "OK: reservation created",}
    result = after_tools(state)
    assert result == "success"

# ---------------------------------------------------------
# TEST 4
# Negative IDs rejected
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
                        "test-token"}},)
# TEST 5
# Zero ID rejected
def test_reserve_rejects_zero_id():
    with pytest.raises(
        ValidationError ):
        reserve_book.invoke({
                "book_id": 0 },
            config={
                "configurable": {
                    "user_token":
                        "test-token"}},)


# ---------------------------------------------------------
# TEST 6
# HTTP 409 -> ERROR_FINAL
@respx.mock
def test_reserve_maps_409_to_final_error():
    respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        return_value=Response(
            409,
            json={
                "message":
                    "Book already reserved"},))
    result = reserve_book.invoke(
        {
            "book_id": 4 },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "pytest-key",}},)
    assert result.startswith(
        "ERROR_FINAL")

# TEST 7
# HTTP 404 -> ERROR_FINAL
@respx.mock
def test_reserve_maps_404_to_final_error():
    respx.post(
        f"{DOTNET_URL}/api/Books/999999/reserve"
    ).mock(
        return_value=Response(
            404,
            json={
                "message":
                    "Book not found"},))
    result = reserve_book.invoke(
        {
            "book_id": 999999
        },
        config={
            "configurable": {
                "user_token":
                    "test-token",
                "idempotency_key":
                    "pytest-key",}},)
    assert result.startswith(
        "ERROR_FINAL"
    )
# ---------------------------------------------------------
# TEST 8
# HTTP 401 -> ERROR_FINAL
@respx.mock
def test_reserve_maps_401_to_final_error():
    respx.post(
        f"{DOTNET_URL}/api/Books/4/reserve"
    ).mock(
        return_value=Response(
            401) )

    result = reserve_book.invoke(
        {
            "book_id": 4},
        config={
            "configurable": {
                "user_token":
                    "bad-token",
                "idempotency_key":
                    "pytest-key",}}, )
    assert result.startswith(
        "ERROR_FINAL")