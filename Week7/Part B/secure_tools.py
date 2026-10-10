import uuid

import httpx

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field


DOTNET_URL = "http://localhost:5194"


class ReserveArgs(BaseModel):
    book_id: int = Field(
        gt=0,
        description="Numeric ID of the book to reserve",
    )


@tool(args_schema=ReserveArgs)
def reserve_book(
    book_id: int,
    config: RunnableConfig,
) -> str:
    """
    Reserve a book for the CURRENT USER.

    Only call this tool after the user has clearly asked
    to reserve a specific book.

    This tool changes data.
    """

    configurable = config.get(
        "configurable",
        {},
    )

    token = configurable.get(
        "user_token"
    )

    if not token:
        return (
            "ERROR_FINAL: missing user authentication token."
        )

    base_key = configurable.get(
        "idempotency_key"
    )

    if not base_key:
        base_key = str(
            uuid.uuid4()
        )

    idempotency_key = (
        f"{base_key}:{book_id}"
    )

    try:
        response = httpx.post(
            f"{DOTNET_URL}/api/Books/{book_id}/reserve",
            headers={
                "Authorization":
                    f"Bearer {token}",

                "Idempotency-Key":
                    idempotency_key,
            },
            timeout=8.0,
        )

    except httpx.TimeoutException:
        return (
            "ERROR_RETRYABLE: "
            "the library service timed out."
        )

    except httpx.RequestError:
        return (
            "ERROR_RETRYABLE: "
            "the library service could not be reached."
        )

    if response.status_code == 409:
        return (
            "ERROR_FINAL: "
            "that book is already reserved."
        )

    if response.status_code in (
        401,
        403,
    ):
        return (
            "ERROR_FINAL: "
            "you are not allowed to do that."
        )

    if response.status_code == 404:
        return (
            "ERROR_FINAL: "
            "no such book."
        )

    if response.status_code == 400:
        return (
            "ERROR_FINAL: "
            "the reservation request was invalid."
        )

    if not response.is_success:
        return (
            f"ERROR_RETRYABLE: "
            f"library service returned "
            f"HTTP {response.status_code}."
        )

    data = response.json()

    return (
        "OK: reservation created. "
        f"Reservation ID: "
        f"{data.get('reservationId')}, "
        f"Book ID: "
        f"{data.get('bookId')}, "
        f"Title: "
        f"{data.get('title')}."
    )