from typing import Annotated, TypedDict

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.graph.message import add_messages


MAX_RETRIES = 2


# ---------------------------------------------------------
# STATE
# ---------------------------------------------------------

class RetryState(TypedDict):
    messages: Annotated[
        list,
        add_messages,
    ]

    retries: int

    plan: list[str]

    tool_result: str


# ---------------------------------------------------------
# PLAN
# ---------------------------------------------------------

def planner_node(
    state: RetryState,
):

    plan = [
        "Identify the requested book.",
        "Attempt the reservation.",
        "Handle any tool error.",
        "Return a clear result.",
    ]

    return {
        "plan": plan,
        "messages": [
            AIMessage(
                content=(
                    "Plan created for the requested action."
                )
            )
        ],
    }


# ---------------------------------------------------------
# SIMULATED TOOL
def tool_node(
    state: RetryState,
):

    result = (
        "ERROR_RETRYABLE: "
        "the library service timed out."
    )

    return {
        "tool_result": result,
        "messages": [
            AIMessage(
                content=result
            )
        ],
    }
    # Normal successful result for baseline testing.
    result = (
        "OK: reservation created."
    )
    return {
        "tool_result": result,
        "messages": [
            AIMessage(
                content=result
            )
        ],
    }


# ---------------------------------------------------------
# DECIDE WHAT TO DO AFTER TOOL
# ---------------------------------------------------------

def after_tools(
    state: RetryState,
):

    result = state["tool_result"]

    if result.startswith(
        "ERROR_RETRYABLE"
    ):
        if state["retries"] < MAX_RETRIES:
            return "retry"

        return "retry_limit"

    if result.startswith(
        "ERROR_CONFLICT"
    ):
        return "replan"

    if result.startswith(
        "ERROR_FINAL"
    ):
        return "stop"

    return "success"


# ---------------------------------------------------------
# RETRY
# ---------------------------------------------------------

def retry_node(
    state: RetryState,
):

    new_retry_count = (
        state["retries"] + 1
    )

    return {
        "retries": new_retry_count,
        "messages": [
            AIMessage(
                content=(
                    "Transient failure detected. "
                    f"Retrying operation "
                    f"({new_retry_count}/{MAX_RETRIES})."
                )
            )
        ],
    }


# ---------------------------------------------------------
# RE-PLAN
# ---------------------------------------------------------

def replan_node(
    state: RetryState,
):

    new_plan = [
        "Reservation conflict detected.",
        "Search for another available book.",
        "Offer the alternative to the user.",
    ]

    return {
        "plan": new_plan,
        "messages": [
            AIMessage(
                content=(
                    "The original plan cannot continue "
                    "because of a conflict. "
                    "I will create a new plan."
                )
            )
        ],
    }


# ---------------------------------------------------------
# SUCCESS
# ---------------------------------------------------------

def success_node(
    state: RetryState,
):

    return {
        "messages": [
            AIMessage(
                content=(
                    "The requested action completed "
                    "successfully."
                )
            )
        ]
    }


# ---------------------------------------------------------
# FINAL ERROR
# ---------------------------------------------------------

def stop_node(
    state: RetryState,
):

    return {
        "messages": [
            AIMessage(
                content=(
                    "The action cannot continue because "
                    "of a final error. "
                    "No retry will be attempted."
                )
            )
        ]
    }


# ---------------------------------------------------------
# RETRY LIMIT
# ---------------------------------------------------------

def retry_limit_node(
    state: RetryState,
):

    return {
        "messages": [
            AIMessage(
                content=(
                    "The service is still unavailable "
                    "after the maximum number of retries. "
                    "Please try again later."
                )
            )
        ]
    }


# ---------------------------------------------------------
# AFTER REPLAN
# ---------------------------------------------------------

def alternative_node(
    state: RetryState,
):

    return {
        "messages": [
            AIMessage(
                content=(
                    "I would now search for another "
                    "available book and offer it "
                    "instead."
                )
            )
        ]
    }


# ---------------------------------------------------------
# GRAPH
# ---------------------------------------------------------

builder = StateGraph(
    RetryState
)


builder.add_node(
    "planner",
    planner_node,
)

builder.add_node(
    "tool",
    tool_node,
)

builder.add_node(
    "retry",
    retry_node,
)

builder.add_node(
    "replan",
    replan_node,
)

builder.add_node(
    "alternative",
    alternative_node,
)

builder.add_node(
    "success",
    success_node,
)

builder.add_node(
    "stop",
    stop_node,
)

builder.add_node(
    "retry_limit",
    retry_limit_node,
)


builder.add_edge(
    START,
    "planner",
)

builder.add_edge(
    "planner",
    "tool",
)


builder.add_conditional_edges(
    "tool",
    after_tools,
    {
        "retry":
            "retry",

        "replan":
            "replan",

        "stop":
            "stop",

        "success":
            "success",

        "retry_limit":
            "retry_limit",
    },
)


builder.add_edge(
    "retry",
    "tool",
)

builder.add_edge(
    "replan",
    "alternative",
)

builder.add_edge(
    "alternative",
    END,
)

builder.add_edge(
    "success",
    END,
)

builder.add_edge(
    "stop",
    END,
)

builder.add_edge(
    "retry_limit",
    END,
)


app = builder.compile()


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    result = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Reserve book 2005 for me."
                    )
                )
            ],
            "retries": 0,
            "plan": [],
            "tool_result": "",
        }
    )

    print()
    print("=" * 60)

    print(
        "PART C - RETRY / REPLAN BASELINE"
    )

    print("=" * 60)

    print(
        "Retries:",
        result["retries"],
    )

    print(
        "Plan:",
        result["plan"],
    )

    print()

    print(
        "MESSAGE TRACE"
    )

    print("-" * 60)

    for index, message in enumerate(
        result["messages"],
        start=1,
    ):
        print(
            f"{index}. {message.content}"
        )

    print()
    print(
        "MERMAID GRAPH"
    )

    print("-" * 60)

    print(
        app.get_graph().draw_mermaid()
    )