import time

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_ollama import ChatOllama

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from langgraph.graph.message import add_messages

from pydantic import BaseModel


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

MAX_GLOBAL_STEPS = 6


# ---------------------------------------------------------
# STATE
# ---------------------------------------------------------

class MultiAgentState(TypedDict):
    messages: Annotated[
        list,
        add_messages,
    ]

    next: str

    steps: int

    model_calls: int

    selected_book_id: int | None

    selected_book_title: str | None

    book_available: bool | None

    reservation_complete: bool


# ---------------------------------------------------------
# SUPERVISOR SCHEMA
# ---------------------------------------------------------

class Next(BaseModel):
    next: Literal[
        "catalog_agent",
        "circulation_agent",
        "FINISH",
    ]


# ---------------------------------------------------------
# MODEL
# ---------------------------------------------------------

model = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


# ---------------------------------------------------------
# DEMO CATALOG
# ---------------------------------------------------------

BOOKS = [
    {
        "id": 1,
        "title": "Dune",
        "genre": "science fiction",
        "available": True,
    },
    {
        "id": 2,
        "title": "Foundation",
        "genre": "science fiction",
        "available": False,
    },
    {
        "id": 3,
        "title": "Clean Code",
        "genre": "software engineering",
        "available": True,
    },
]


# ---------------------------------------------------------
# SUPERVISOR
# ---------------------------------------------------------

SUPERVISOR_PROMPT = """
You are the supervisor of a library multi-agent system.

There are two specialist agents:

1. catalog_agent
   - read-only
   - finds books
   - checks availability
   - cannot reserve books

2. circulation_agent
   - handles reservations
   - write-capable
   - should only act after a suitable available book
     has already been identified

Choose:

catalog_agent
when the task still requires finding or checking a book.

circulation_agent
when an available book has already been identified and
the remaining task is to reserve it.

FINISH
when the user's full request has been completed.

Never send a reservation task to catalog_agent.
Never ask circulation_agent to discover books.
"""


supervisor_router = model.with_structured_output(
    Next
)


def supervisor_node(
    state: MultiAgentState,
):

    if state["steps"] >= MAX_GLOBAL_STEPS:
        return {
            "next": "FINISH",
            "steps": state["steps"],
            "model_calls":
                state["model_calls"],
            "messages": [
                AIMessage(
                    content=(
                        "Global step limit reached. "
                        "Stopping the multi-agent workflow."
                    )
                )
            ],
        }

    result = supervisor_router.invoke(
        [
            SystemMessage(
                content=SUPERVISOR_PROMPT
            ),
            *state["messages"],
        ]
    )

    new_steps = (
        state["steps"] + 1
    )

    new_calls = (
        state["model_calls"] + 1
    )

    print(
        f"SUPERVISOR DECISION "
        f"{new_steps}: {result.next}"
    )

    return {
        "next": result.next,
        "steps": new_steps,
        "model_calls": new_calls,
    }


# ---------------------------------------------------------
# CATALOG AGENT
# ---------------------------------------------------------

def catalog_agent_node(
    state: MultiAgentState,
):

    model_response = model.invoke(
        [
            SystemMessage(
                content=(
                    "You are the Catalog Agent. "
                    "You only perform read operations. "
                    "You find suitable books and check "
                    "availability. You cannot reserve books."
                )
            ),
            state["messages"][0],
        ]
    )

    model_calls = (
        state["model_calls"] + 1
    )

    selected = None

    for book in BOOKS:
        if (
            book["genre"]
            == "science fiction"
            and book["available"]
        ):
            selected = book
            break

    if selected is None:
        return {
            "messages": [
                AIMessage(
                    content=(
                        "CATALOG AGENT: "
                        "No available science fiction "
                        "book was found."
                    )
                )
            ],
            "model_calls": model_calls,
        }

    return {
        "selected_book_id":
            selected["id"],

        "selected_book_title":
            selected["title"],

        "book_available":
            selected["available"],

        "messages": [
            AIMessage(
                content=(
                    "CATALOG AGENT: "
                    f"Found {selected['title']} "
                    f"(Book ID {selected['id']}) "
                    "and it is available."
                )
            )
        ],

        "model_calls":
            model_calls,
    }


# ---------------------------------------------------------
# CIRCULATION AGENT
# ---------------------------------------------------------

def circulation_agent_node(
    state: MultiAgentState,
):

    model_response = model.invoke(
        [
            SystemMessage(
                content=(
                    "You are the Circulation Agent. "
                    "You handle reservation actions only. "
                    "You must never search the catalog."
                )
            ),
            *state["messages"],
        ]
    )

    model_calls = (
        state["model_calls"] + 1
    )

    book_id = state.get(
        "selected_book_id"
    )

    title = state.get(
        "selected_book_title"
    )

    available = state.get(
        "book_available"
    )

    if (
        book_id is None
        or not available
    ):
        return {
            "messages": [
                AIMessage(
                    content=(
                        "CIRCULATION AGENT: "
                        "No confirmed available book "
                        "was provided, so I will not "
                        "perform a reservation."
                    )
                )
            ],
            "reservation_complete":
                False,
            "model_calls":
                model_calls,
        }

    return {
        "messages": [
            AIMessage(
                content=(
                    "CIRCULATION AGENT: "
                    f"Reserved {title} "
                    f"(Book ID {book_id})."
                )
            )
        ],

        "reservation_complete":
            True,

        "model_calls":
            model_calls,
    }


# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------

def route_from_supervisor(
    state: MultiAgentState,
):

    if state["steps"] >= MAX_GLOBAL_STEPS:
        return "FINISH"

    return state["next"]


# ---------------------------------------------------------
# GRAPH
# ---------------------------------------------------------

builder = StateGraph(
    MultiAgentState
)


builder.add_node(
    "supervisor",
    supervisor_node,
)

builder.add_node(
    "catalog_agent",
    catalog_agent_node,
)

builder.add_node(
    "circulation_agent",
    circulation_agent_node,
)


builder.add_edge(
    START,
    "supervisor",
)


builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "catalog_agent":
            "catalog_agent",

        "circulation_agent":
            "circulation_agent",

        "FINISH":
            END,
    },
)


builder.add_edge(
    "catalog_agent",
    "supervisor",
)

builder.add_edge(
    "circulation_agent",
    "supervisor",
)


app = builder.compile()


# ---------------------------------------------------------
# TEST RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    question = (
        "Find me an available sci-fi book "
        "and reserve it."
    )

    print()
    print(
        "=" * 70
    )

    print(
        "PART E - MULTI-AGENT TEST"
    )

    print(
        "=" * 70
    )

    print(
        "User:",
        question,
    )

    start_time = time.perf_counter()

    result = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content=question
                )
            ],

            "next": "",

            "steps": 0,

            "model_calls": 0,

            "selected_book_id":
                None,

            "selected_book_title":
                None,

            "book_available":
                None,

            "reservation_complete":
                False,
        },

        config={
            "recursion_limit": 20
        },
    )

    end_time = time.perf_counter()

    elapsed = (
        end_time - start_time
    )

    print()
    print(
        "=" * 70
    )

    print(
        "FINAL MESSAGE TRACE"
    )

    print(
        "=" * 70
    )

    for index, message in enumerate(
        result["messages"],
        start=1,
    ):
        print(
            f"{index}. "
            f"{message.content}"
        )

    print()
    print(
        "Global steps:",
        result["steps"],
    )

    print(
        "Model calls:",
        result["model_calls"],
    )

    print(
        "Reservation complete:",
        result["reservation_complete"],
    )

    print(
        f"Elapsed time: "
        f"{elapsed:.2f} seconds"
    )

    print()
    print(
        "MERMAID GRAPH"
    )

    print(
        app
        .get_graph()
        .draw_mermaid()
    )