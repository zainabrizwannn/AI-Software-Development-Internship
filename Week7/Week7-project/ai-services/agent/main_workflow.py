import re

from typing import (
    Annotated,
    Literal,
    TypedDict,
)

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from langchain_core.runnables import (
    RunnableConfig,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.graph.message import (
    add_messages,
)
from langgraph.types import (
    Command,
    interrupt,
)

from secure_tools import (
    check_availability,
    list_my_reservations,
    reserve_book,
    search_catalog,
)


MAX_STEPS = 10
MAX_RETRIES = 2


# =========================================================
# STATE
# =========================================================

class AgentState(TypedDict):
    messages: Annotated[
        list,
        add_messages,
    ]

    route: str

    steps: int

    retries: int

    selected_book_id: int | None

    tool_result: str

    final_answer: str


# =========================================================
# HELPERS
# =========================================================

def latest_user_text(
    state: AgentState,
) -> str:

    for message in reversed(
        state["messages"]
    ):
        if isinstance(
            message,
            HumanMessage,
        ):
            return str(
                message.content
            )

    return ""


def extract_book_id(
    text: str,
) -> int | None:

    match = re.search(
        r"\b(\d+)\b",
        text,
    )

    if not match:
        return None

    value = int(
        match.group(1)
    )

    if value <= 0:
        return None

    return value


def step_limit_reached(
    state: AgentState,
) -> bool:

    return (
        state.get(
            "steps",
            0,
        )
        >= MAX_STEPS
    )


# =========================================================
# ROUTER
# =========================================================

def router_node(
    state: AgentState,
):

    text = (
        latest_user_text(
            state
        )
        .lower()
    )

    if any(
        phrase in text
        for phrase in (
            "my reservations",
            "list reservations",
            "show reservations",
            "what have i reserved",
        )
    ):
        route = (
            "list_reservations"
        )

    elif any(
        word in text
        for word in (
            "reserve",
            "book it",
            "book this",
        )
    ):
        route = "action"

    elif any(
        word in text
        for word in (
            "book",
            "author",
            "available",
            "catalog",
            "find",
            "search",
            "recommend",
        )
    ):
        route = "catalog"

    else:
        route = "chitchat"

    return {
        "route":
            route,

        "steps":
            state.get(
                "steps",
                0,
            )
            + 1,
    }


def route_after_router(
    state: AgentState,
) -> str:
    return state["route"]


# =========================================================
# CATALOG
# =========================================================

def catalog_node(
    state: AgentState,
    config: RunnableConfig,
):

    if step_limit_reached(
        state
    ):
        return {
            "final_answer":
                "The agent stopped because "
                "the step limit was reached.",

            "messages": [
                AIMessage(
                    content=(
                        "The agent stopped because "
                        "the step limit was reached."
                    )
                )
            ],
        }

    text = latest_user_text(
        state
    )

    result = search_catalog.invoke(
        {
            "query":
                text
        },
        config=config,
    )

    answer = (
        "Catalog search result: "
        f"{result}"
    )

    return {
        "tool_result":
            result,

        "final_answer":
            answer,

        "steps":
            state["steps"] + 1,

        "messages": [
            AIMessage(
                content=answer
            )
        ],
    }


# =========================================================
# LIST MY RESERVATIONS
# =========================================================

def reservations_node(
    state: AgentState,
    config: RunnableConfig,
):

    result = (
        list_my_reservations
        .invoke(
            {},
            config=config,
        )
    )

    answer = (
        "Your reservation result: "
        f"{result}"
    )

    return {
        "tool_result":
            result,

        "final_answer":
            answer,

        "steps":
            state["steps"] + 1,

        "messages": [
            AIMessage(
                content=answer
            )
        ],
    }


# =========================================================
# ACTION PREPARATION
# =========================================================

def prepare_action_node(
    state: AgentState,
    config: RunnableConfig,
):

    if step_limit_reached(
        state
    ):
        answer = (
            "The agent stopped because "
            "the step limit was reached."
        )

        return Command(
            goto="final",
            update={
                "final_answer":
                    answer
            },
        )

    user_text = latest_user_text(
        state
    )

    book_id = extract_book_id(
        user_text
    )

    # Search happens before the check so the timeline
    # represents find -> check -> approval.
    search_result = (
        search_catalog.invoke(
            {
                "query": ""
            },
            config=config,
        )
    )

    if book_id is None:

        answer = (
            "I searched the catalog, but I need "
            "a specific numeric book ID before "
            "I can request reservation approval."
        )

        return Command(
            goto="final",
            update={
                "tool_result":
                    search_result,

                "final_answer":
                    answer,

                "steps":
                    state["steps"]
                    + 1,
            },
        )

    return {
        "selected_book_id":
            book_id,

        "tool_result":
            search_result,

        "steps":
            state["steps"]
            + 1,
    }


# =========================================================
# AVAILABILITY
# =========================================================

def availability_node(
    state: AgentState,
    config: RunnableConfig,
):

    book_id = state.get(
        "selected_book_id"
    )

    if not book_id:
        return Command(
            goto="final",
            update={
                "final_answer":
                    "No book ID was selected."
            },
        )

    result = (
        check_availability
        .invoke(
            {
                "book_id":
                    book_id
            },
            config=config,
        )
    )

    update = {
        "tool_result":
            result,

        "steps":
            state["steps"] + 1,
    }

    if result.startswith(
        "ERROR_CONFLICT"
    ):
        return Command(
            goto="replan",
            update=update,
        )

    if result.startswith(
        "ERROR_RETRYABLE"
    ):
        if (
            state.get(
                "retries",
                0,
            )
            < MAX_RETRIES
        ):
            update[
                "retries"
            ] = (
                state.get(
                    "retries",
                    0,
                )
                + 1
            )

            return Command(
                goto="availability",
                update=update,
            )

    if result.startswith(
        "ERROR_"
    ):
        return Command(
            goto="final",
            update={
                **update,

                "final_answer":
                    result,
            },
        )

    return Command(
        goto="approval",
        update=update,
    )


# =========================================================
# HUMAN APPROVAL
# =========================================================

def approval_node(
    state: AgentState,
):

    book_id = state[
        "selected_book_id"
    ]

    decision = interrupt(
        {
            "type":
                "approval_required",

            "calls": [
                {
                    "name":
                        "reserve_book",

                    "args": {
                        "book_id":
                            book_id
                    },
                }
            ],
        }
    )

    approved = (
        isinstance(
            decision,
            dict,
        )
        and decision.get(
            "approved"
        )
        is True
    )

    if approved:
        return Command(
            goto="reserve"
        )

    return Command(
        goto="final",
        update={
            "final_answer":
                (
                    "The reservation was not made "
                    "because you rejected the action."
                )
        },
    )


# =========================================================
# REAL RESERVATION TOOL
# =========================================================

def reserve_node(
    state: AgentState,
    config: RunnableConfig,
):

    if step_limit_reached(
        state
    ):
        return Command(
            goto="final",
            update={
                "final_answer":
                    (
                        "The agent stopped because "
                        "the step limit was reached."
                    )
            },
        )

    book_id = state[
        "selected_book_id"
    ]

    result = reserve_book.invoke(
        {
            "book_id":
                book_id
        },
        config=config,
    )

    update = {
        "tool_result":
            result,

        "steps":
            state["steps"] + 1,
    }

    if result.startswith(
        "OK:"
    ):
        return Command(
            goto="success",
            update=update,
        )

    if result.startswith(
        "ERROR_CONFLICT"
    ):
        return Command(
            goto="replan",
            update=update,
        )

    if result.startswith(
        "ERROR_RETRYABLE"
    ):
        retries = state.get(
            "retries",
            0,
        )

        if retries < MAX_RETRIES:

            update[
                "retries"
            ] = retries + 1

            return Command(
                goto="reserve",
                update=update,
            )

    return Command(
        goto="final",
        update={
            **update,

            "final_answer":
                result,
        },
    )


# =========================================================
# RE-PLAN
# =========================================================

def replan_node(
    state: AgentState,
    config: RunnableConfig,
):

    catalog = search_catalog.invoke(
        {
            "query": ""
        },
        config=config,
    )

    answer = (
        "The selected book is no longer "
        "available, so I re-planned instead "
        "of repeatedly attempting the same "
        "reservation. "
        f"Other catalog options: {catalog}"
    )

    return {
        "final_answer":
            answer,

        "tool_result":
            catalog,

        "steps":
            state["steps"] + 1,

        "messages": [
            AIMessage(
                content=answer
            )
        ],
    }


# =========================================================
# SUCCESS
# =========================================================

def success_node(
    state: AgentState,
):

    answer = (
        "Reservation completed successfully. "
        f"{state.get('tool_result', '')}"
    )

    return {
        "final_answer":
            answer,

        "messages": [
            AIMessage(
                content=answer
            )
        ],
    }


# =========================================================
# CHITCHAT
# =========================================================

def chitchat_node(
    state: AgentState,
):

    answer = (
        "Hello! I can help you find books, "
        "check availability, view your "
        "reservations, and safely reserve a book."
    )

    return {
        "final_answer":
            answer,

        "messages": [
            AIMessage(
                content=answer
            )
        ],

        "steps":
            state["steps"] + 1,
    }


# =========================================================
# FINAL
# =========================================================

def final_node(
    state: AgentState,
):

    answer = (
        state.get(
            "final_answer"
        )
        or state.get(
            "tool_result"
        )
        or (
            "The request could not "
            "be completed."
        )
    )

    return {
        "messages": [
            AIMessage(
                content=answer
            )
        ],
    }


# =========================================================
# GRAPH
# =========================================================

builder = StateGraph(
    AgentState
)

builder.add_node(
    "router",
    router_node,
)

builder.add_node(
    "catalog",
    catalog_node,
)

builder.add_node(
    "list_reservations",
    reservations_node,
)

builder.add_node(
    "prepare_action",
    prepare_action_node,
)

builder.add_node(
    "availability",
    availability_node,
)

builder.add_node(
    "approval",
    approval_node,
)

builder.add_node(
    "reserve",
    reserve_node,
)

builder.add_node(
    "replan",
    replan_node,
)

builder.add_node(
    "success",
    success_node,
)

builder.add_node(
    "chitchat",
    chitchat_node,
)

builder.add_node(
    "final",
    final_node,
)


builder.add_edge(
    START,
    "router",
)

builder.add_conditional_edges(
    "router",
    route_after_router,
    {
        "catalog":
            "catalog",

        "action":
            "prepare_action",

        "list_reservations":
            "list_reservations",

        "chitchat":
            "chitchat",
    },
)

builder.add_edge(
    "catalog",
    END,
)

builder.add_edge(
    "list_reservations",
    END,
)

builder.add_edge(
    "prepare_action",
    "availability",
)

builder.add_edge(
    "replan",
    END,
)

builder.add_edge(
    "success",
    END,
)

builder.add_edge(
    "chitchat",
    END,
)

builder.add_edge(
    "final",
    END,
)