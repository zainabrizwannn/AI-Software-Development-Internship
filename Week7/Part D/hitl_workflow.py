from typing import Annotated, TypedDict

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.graph.message import add_messages
from langgraph.types import (
    Command,
    interrupt,
)


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

CHECKPOINT_DB = "agent_checkpoints.sqlite"

RISKY_TOOLS = {
    "reserve_book",
}


# ---------------------------------------------------------
# STATE
# ---------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[
        list,
        add_messages,
    ]

    steps: int

    retries: int


# ---------------------------------------------------------
# AGENT NODE
# ---------------------------------------------------------

def agent_node(
    state: AgentState,
):
    """
    Simulated agent node for Part D.

    It creates a risky reserve_book tool call so we can
    demonstrate HITL approval and persistence clearly.
    """

    already_has_tool_result = any(
        isinstance(message, ToolMessage)
        for message in state["messages"]
    )

    if already_has_tool_result:
        last_tool_result = next(
            (
                message.content
                for message in reversed(
                    state["messages"]
                )
                if isinstance(
                    message,
                    ToolMessage,
                )
            ),
            "",
        )

        if (
            last_tool_result
            == "REJECTED_BY_USER"
        ):
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "The reservation was not made "
                            "because you rejected the action."
                        )
                    )
                ],
                "steps":
                    state["steps"] + 1,
            }

        return {
            "messages": [
                AIMessage(
                    content=(
                        "The reservation action completed."
                    )
                )
            ],
            "steps":
                state["steps"] + 1,
        }

    tool_call = {
        "name":
            "reserve_book",

        "args":
            {
                "book_id": 2005
            },

        "id":
            "reserve-call-001",

        "type":
            "tool_call",
    }

    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    tool_call
                ],
            )
        ],
        "steps":
            state["steps"] + 1,
    }


# ---------------------------------------------------------
# APPROVAL NODE
# ---------------------------------------------------------

def approval_node(
    state: AgentState,
):
    last_message = (
        state["messages"][-1]
    )

    risky_calls = [
        call
        for call in (
            last_message.tool_calls
        )
        if call["name"]
        in RISKY_TOOLS
    ]

    if not risky_calls:
        return Command(
            goto="tools"
        )

    decision = interrupt(
        {
            "type":
                "approval_required",

            "calls":
                risky_calls,
        }
    )

    if (
        isinstance(
            decision,
            dict,
        )
        and decision.get(
            "approved"
        ) is True
    ):
        return Command(
            goto="tools"
        )

    rejections = [
        ToolMessage(
            content=
                "REJECTED_BY_USER",

            tool_call_id=
                call["id"],
        )
        for call in (
            last_message.tool_calls
        )
    ]

    return Command(
        goto="agent",
        update={
            "messages":
                rejections
        },
    )


# ---------------------------------------------------------
# TOOLS NODE
# ---------------------------------------------------------

def tools_node(
    state: AgentState,
):
    """
    Simulated secure write tool execution.

    We intentionally do not store any JWT in graph state.
    In a real flow, the JWT would come from RunnableConfig.
    """

    last_message = (
        state["messages"][-1]
    )

    tool_messages = []

    for call in (
        last_message.tool_calls
    ):
        if (
            call["name"]
            == "reserve_book"
        ):
            book_id = (
                call["args"][
                    "book_id"
                ]
            )

            tool_messages.append(
                ToolMessage(
                    content=(
                        "OK: reservation "
                        f"created for book "
                        f"{book_id}."
                    ),
                    tool_call_id=
                        call["id"],
                )
            )

    return {
        "messages":
            tool_messages,
    }


# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------

def route_after_agent(
    state: AgentState,
):
    last_message = (
        state["messages"][-1]
    )

    if (
        isinstance(
            last_message,
            AIMessage,
        )
        and last_message.tool_calls
    ):
        return "approval"

    return END


# ---------------------------------------------------------
# BUILD GRAPH
# ---------------------------------------------------------

builder = StateGraph(
    AgentState
)


builder.add_node(
    "agent",
    agent_node,
)

builder.add_node(
    "approval",
    approval_node,
)

builder.add_node(
    "tools",
    tools_node,
)


builder.add_edge(
    START,
    "agent",
)


builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "approval":
            "approval",

        END:
            END,
    },
)


builder.add_edge(
    "tools",
    "agent",
)


# ---------------------------------------------------------
# RUN WITH SQLITE CHECKPOINTER
# ---------------------------------------------------------

def print_messages(
    messages,
):
    print()
    print(
        "=" * 60
    )

    print(
        "MESSAGE TRACE"
    )

    print(
        "=" * 60
    )

    for index, message in enumerate(
        messages,
        start=1,
    ):
        print()

        print(
            f"{index}. "
            f"{type(message).__name__}"
        )

        if (
            isinstance(
                message,
                AIMessage,
            )
            and message.tool_calls
        ):
            print(
                "Tool calls:",
                message.tool_calls,
            )

        else:
            print(
                "Content:",
                message.content,
            )


if __name__ == "__main__":

    thread_id = (
        "u1002:part-d-demo"
    )

    config = {
        "configurable":
            {
                "thread_id":
                    thread_id,

                # Demonstration only:
                # token stays in config,
                # NOT inside graph state.
                "user_token":
                    "DEMO_TOKEN_NOT_STORED_IN_STATE",
            }
    }

    with SqliteSaver.from_conn_string(
        CHECKPOINT_DB
    ) as saver:

        app = builder.compile(
            checkpointer=saver
        )

        print()
        print(
            "PART D - HITL / CHECKPOINT DEMO"
        )

        print(
            "Thread ID:",
            thread_id,
        )

        print()
        print(
            "Starting graph..."
        )

        result = app.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            "Reserve book 2005 "
                            "for me."
                        )
                    )
                ],
                "steps": 0,
                "retries": 0,
            },
            config,
        )

        print()
        print(
            "Graph paused."
        )

        print(
            "Raw result:",
            result,
        )

        print()
        print(
            "If an approval interrupt "
            "appeared above, the pause "
            "worked correctly."
        )