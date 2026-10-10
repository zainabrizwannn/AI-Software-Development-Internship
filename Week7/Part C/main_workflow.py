from typing import Annotated, Literal, TypedDict

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel


# ---------------------------------------------------------
# STATE
# ---------------------------------------------------------

class WorkflowState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str
    retries: int
    plan: list[str]


# ---------------------------------------------------------
# ROUTE SCHEMA
# ---------------------------------------------------------

class Route(BaseModel):
    route: Literal[
        "catalog",
        "action",
        "chitchat",
    ]


# ---------------------------------------------------------
# MODEL
# ---------------------------------------------------------

model = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------

ROUTER_PROMPT = """
You are a routing classifier for a library assistant.

Choose exactly one route:

catalog:
- book information
- availability
- authors
- categories
- recommendations
- finding books

action:
- reserve
- cancel
- update
- any request that changes data

chitchat:
- greetings
- thanks
- casual conversation
- non-library small talk

Return only:
catalog
action
chitchat
"""


router = model.with_structured_output(
    Route
)


def router_node(
    state: WorkflowState,
):
    last_message = state["messages"][-1]

    result = router.invoke(
        [
            SystemMessage(
                content=ROUTER_PROMPT
            ),
            last_message,
        ]
    )

    return {
        "route": result.route
    }


# ---------------------------------------------------------
# CATALOG BRANCH
# ---------------------------------------------------------

def rag_subgraph_node(
    state: WorkflowState,
):
    user_text = (
        state["messages"][-1].content
    )

    # Temporary Part C wrapper around the Week 6 RAG path.
    # The full Week 6 implementation can be plugged in here.
    reply = (
        "CATALOG BRANCH: "
        f"Week 6 RAG should answer: {user_text}"
    )

    return {
        "messages": [
            AIMessage(
                content=reply
            )
        ]
    }


# ---------------------------------------------------------
# ACTION BRANCH
# ---------------------------------------------------------

def planner_node(
    state: WorkflowState,
):
    user_text = (
        state["messages"][-1].content
    )

    plan = [
        "Identify the requested action.",
        "Check required book information.",
        "Execute the write tool securely.",
        "Return the result to the user.",
    ]

    return {
        "plan": plan,
        "messages": [
            AIMessage(
                content=(
                    "ACTION BRANCH: "
                    f"Created plan for: {user_text}"
                )
            )
        ],
    }


def action_executor_node(
    state: WorkflowState,
):
    return {
        "messages": [
            AIMessage(
                content=(
                    "Action execution placeholder. "
                    "Secure reservation tool will run here."
                )
            )
        ]
    }


# ---------------------------------------------------------
# CHITCHAT BRANCH
# ---------------------------------------------------------

def small_talk_node(
    state: WorkflowState,
):
    response = model.invoke(
        [
            SystemMessage(
                content=(
                    "Reply briefly and naturally. "
                    "Do not use tools."
                )
            ),
            state["messages"][-1],
        ]
    )

    return {
        "messages": [
            response
        ]
    }


# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------

def route_from_router(
    state: WorkflowState,
):
    return state["route"]


# ---------------------------------------------------------
# GRAPH
# ---------------------------------------------------------

builder = StateGraph(
    WorkflowState
)

builder.add_node(
    "router",
    router_node,
)

builder.add_node(
    "rag_subgraph",
    rag_subgraph_node,
)

builder.add_node(
    "planner",
    planner_node,
)

builder.add_node(
    "action_executor",
    action_executor_node,
)

builder.add_node(
    "small_talk",
    small_talk_node,
)


builder.add_edge(
    START,
    "router",
)


builder.add_conditional_edges(
    "router",
    route_from_router,
    {
        "catalog":
            "rag_subgraph",

        "action":
            "planner",

        "chitchat":
            "small_talk",
    },
)


builder.add_edge(
    "rag_subgraph",
    END,
)

builder.add_edge(
    "planner",
    "action_executor",
)

builder.add_edge(
    "action_executor",
    END,
)

builder.add_edge(
    "small_talk",
    END,
)


app = builder.compile()


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

def run_test(
    question: str,
):
    result = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content=question
                )
            ],
            "route": "",
            "retries": 0,
            "plan": [],
        }
    )

    print()
    print("=" * 60)

    print(
        "Question:",
        question,
    )

    print(
        "Route:",
        result["route"],
    )

    print(
        "Plan:",
        result.get(
            "plan",
            [],
        ),
    )

    print(
        "Final:",
        result["messages"][-1].content,
    )


if __name__ == "__main__":

    run_test(
        "Who wrote Clean Code?"
    )

    run_test(
        "Reserve book 2005 for me."
    )

    run_test(
        "Hello, how are you?"
    )

    print()
    print(
        app
        .get_graph()
        .draw_mermaid()
    )