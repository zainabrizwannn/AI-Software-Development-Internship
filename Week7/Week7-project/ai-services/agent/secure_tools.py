import json
import uuid

import httpx

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from pydantic import BaseModel, Field


DOTNET_URL = "http://localhost:5194"


# =========================================================
# ARGUMENT MODELS
# =========================================================

class SearchArgs(BaseModel):
    query: str = Field(
        default="",
        description="Book title, author, category, or search text.",
    )


class BookIdArgs(BaseModel):
    book_id: int = Field(
        gt=0,
        description="Positive numeric book ID.",
    )


# =========================================================
# HELPERS
# =========================================================

def _configurable(
    config: RunnableConfig,
) -> dict:
    return config.get(
        "configurable",
        {},
    )


def _token(
    config: RunnableConfig,
) -> str | None:
    return _configurable(
        config
    ).get(
        "user_token"
    )


def _auth_headers(
    config: RunnableConfig,
) -> dict[str, str]:
    token = _token(
        config
    )

    if not token:
        return {}

    return {
        "Authorization":
            f"Bearer {token}"
    }


def _normalise_books(
    payload,
) -> list[dict]:

    if isinstance(
        payload,
        list,
    ):
        return payload

    if isinstance(
        payload,
        dict,
    ):
        for key in (
            "items",
            "books",
            "data",
            "results",
        ):
            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

    return []


def _value(
    item: dict,
    *names,
):
    for name in names:
        if name in item:
            return item[name]

    return None


# =========================================================
# SEARCH CATALOG
# =========================================================

@tool(args_schema=SearchArgs)
def search_catalog(
    query: str,
    config: RunnableConfig,
) -> str:
    """
    Search the library catalog.

    This is a read-only operation.
    """

    try:
        response = httpx.get(
            f"{DOTNET_URL}/api/Books",
            headers=_auth_headers(
                config
            ),
            timeout=8.0,
        )

    except httpx.TimeoutException:
        return (
            "ERROR_RETRYABLE: "
            "catalog request timed out."
        )

    except httpx.RequestError:
        return (
            "ERROR_RETRYABLE: "
            "catalog service could not be reached."
        )

    if response.status_code in (
        401,
        403,
    ):
        return (
            "ERROR_FINAL: "
            "catalog access was denied."
        )

    if not response.is_success:
        return (
            "ERROR_RETRYABLE: "
            f"catalog returned HTTP "
            f"{response.status_code}."
        )

    books = _normalise_books(
        response.json()
    )

    query_text = (
        query
        .strip()
        .lower()
    )

    if query_text:
        filtered = []

        for book in books:
            searchable = " ".join(
                str(
                    _value(
                        book,
                        "title",
                        "Title",
                    )
                    or ""
                )
                + " "
                + str(
                    _value(
                        book,
                        "author",
                        "Author",
                        "authorName",
                        "AuthorName",
                    )
                    or ""
                )
                for _ in [0]
            ).lower()

            if (
                query_text
                in searchable
            ):
                filtered.append(
                    book
                )

        books = filtered

    books = books[:10]

    if not books:
        return (
            "OK: no matching books found."
        )

    compact = []

    for book in books:
        compact.append(
            {
                "bookId":
                    _value(
                        book,
                        "bookId",
                        "BookId",
                    ),

                "title":
                    _value(
                        book,
                        "title",
                        "Title",
                    ),

                "isAvailable":
                    _value(
                        book,
                        "isAvailable",
                        "IsAvailable",
                    ),
            }
        )

    return (
        "OK: catalog results: "
        + json.dumps(
            compact,
            ensure_ascii=False,
        )
    )


# =========================================================
# CHECK AVAILABILITY
# =========================================================

@tool(args_schema=BookIdArgs)
def check_availability(
    book_id: int,
    config: RunnableConfig,
) -> str:
    """
    Check whether a book is currently available.

    This is a read-only operation.
    """

    try:
        response = httpx.get(
            f"{DOTNET_URL}/api/Books",
            headers=_auth_headers(
                config
            ),
            timeout=8.0,
        )

    except httpx.TimeoutException:
        return (
            "ERROR_RETRYABLE: "
            "availability check timed out."
        )

    except httpx.RequestError:
        return (
            "ERROR_RETRYABLE: "
            "library service could not be reached."
        )

    if response.status_code in (
        401,
        403,
    ):
        return (
            "ERROR_FINAL: "
            "availability access was denied."
        )

    if not response.is_success:
        return (
            "ERROR_RETRYABLE: "
            f"library service returned "
            f"HTTP {response.status_code}."
        )

    books = _normalise_books(
        response.json()
    )

    for book in books:

        current_id = _value(
            book,
            "bookId",
            "BookId",
        )

        try:
            current_id = int(
                current_id
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        if current_id != book_id:
            continue

        available = _value(
            book,
            "isAvailable",
            "IsAvailable",
        )

        title = _value(
            book,
            "title",
            "Title",
        )

        if available is True:
            return (
                "OK: book is available. "
                f"Book ID: {book_id}, "
                f"Title: {title}."
            )

        return (
            "ERROR_CONFLICT: "
            f"book {book_id} is not available."
        )

    return (
        "ERROR_FINAL: "
        f"book {book_id} was not found."
    )


# =========================================================
# RESERVE
# =========================================================

@tool(args_schema=BookIdArgs)
def reserve_book(
    book_id: int,
    config: RunnableConfig,
) -> str:
    """
    Reserve a book for the CURRENT authenticated user.

    This is a write operation and must only execute
    after human approval.
    """

    configurable = _configurable(
        config
    )

    token = configurable.get(
        "user_token"
    )

    if not token:
        return (
            "ERROR_FINAL: "
            "missing user authentication token."
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
            (
                f"{DOTNET_URL}"
                f"/api/Books/"
                f"{book_id}/reserve"
            ),
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

    # 409 is a conflict so LangGraph can RE-PLAN.
    if response.status_code == 409:
        return (
            "ERROR_CONFLICT: "
            "that book is already reserved "
            "or unavailable."
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
            "ERROR_RETRYABLE: "
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


# =========================================================
# LIST MY RESERVATIONS
# =========================================================

@tool
def list_my_reservations(
    config: RunnableConfig,
) -> str:
    """
    List reservations belonging to the CURRENT user.
    """

    token = _token(
        config
    )

    if not token:
        return (
            "ERROR_FINAL: "
            "missing user authentication token."
        )

    try:
        response = httpx.get(
            (
                f"{DOTNET_URL}"
                "/api/me/reservations"
            ),
            headers={
                "Authorization":
                    f"Bearer {token}"
            },
            timeout=8.0,
        )

    except httpx.TimeoutException:
        return (
            "ERROR_RETRYABLE: "
            "reservation list timed out."
        )

    except httpx.RequestError:
        return (
            "ERROR_RETRYABLE: "
            "library service could not be reached."
        )

    if response.status_code in (
        401,
        403,
    ):
        return (
            "ERROR_FINAL: "
            "you are not allowed to view reservations."
        )

    if not response.is_success:
        return (
            "ERROR_RETRYABLE: "
            f"library service returned "
            f"HTTP {response.status_code}."
        )

    return (
        "OK: reservations: "
        + json.dumps(
            response.json(),
            ensure_ascii=False,
        )
    )