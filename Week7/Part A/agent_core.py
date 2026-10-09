from typing import Annotated, TypedDict

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


# ---------------------------------------------------------
# CONFIGURATION
MAX_STEPS = 6

SYSTEM_PROMPT = """
You are a Library Agent.

Your job is to help the user find books and check whether
they are available.

You have two tools:

1. search_catalog
   Use this when the user asks you to find a book,
   search by genre, or discover books.

2. check_book_availability
   Use this when you need to know whether a specific
   book is currently available.

For a request such as:
"Find a science fiction book and tell me if it is available."

You should:
1. search the catalog,
2. choose a suitable book,
3. check its availability,
4. answer the user clearly.

Do not invent availability information.
Use tools when tool information is required.
"""


# ---------------------------------------------------------
# SIMPLE LIBRARY DATA FOR PART A
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
        "title": "The Alchemist",
        "genre": "fiction",
        "available": False,
    },
    {
        "id": 3,
        "title": "Foundation",
        "genre": "science fiction",
        "available": False,
    },
    {
        "id": 4,
        "title": "Atomic Habits",
        "genre": "self help",
        "available": True,
    },
]


# ---------------------------------------------------------
# TOOLS
# ---------------------------------------------------------

@tool
def search_catalog(query: str) -> str:
    """
    Search the library catalog by title or genre.

    Use this tool when the user wants to find a book,
    discover books in a genre, or search the catalog.
    """

    query_lower = query.lower()

    matches = []

    for book in BOOKS:

        if (
            query_lower in book["title"].lower()
            or query_lower in book["genre"].lower()
            or (
                "science fiction" in query_lower
                and book["genre"] == "science fiction"
            )
        ):
            matches.append(book)

    if not matches:
        return "No matching books were found."

    result_lines = []

    for book in matches:

        result_lines.append(
            f'Book ID {book["id"]}: '
            f'{book["title"]} '
            f'({book["genre"]})'
        )

    return "\n".join(result_lines)


@tool
def check_book_availability(book_id: int) -> str:
    """
    Check whether a specific book is currently available.

    Use this only when the availability of a known book
    needs to be checked.
    """

    for book in BOOKS:

        if book["id"] == book_id:

            if book["available"]:

                return (
                    f'{book["title"]} is currently '
                    f'available.'
                )

            return (
                f'{book["title"]} is currently '
                f'not available.'
            )

    return "Book not found."


TOOLS = [
    search_catalog,
    check_book_availability,
]


# ---------------------------------------------------------
# MODEL
# ---------------------------------------------------------

model = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


model_with_tools = model.bind_tools(
    TOOLS
)


# ---------------------------------------------------------
# LANGGRAPH STATE
# ---------------------------------------------------------

class AgentState(TypedDict):

    messages: Annotated[
        list,
        add_messages,
    ]

    steps: int


# ---------------------------------------------------------
# AGENT NODE
# ---------------------------------------------------------

def agent_node(
    state: AgentState,
):

    reply = model_with_tools.invoke(
        [
            SystemMessage(
                content=SYSTEM_PROMPT
            ),
            *state["messages"],
        ]
    )

    return {
        "messages": [
            reply
        ],
        "steps":
            state["steps"] + 1,
    }


# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------

def route_after_agent(
    state: AgentState,
):

    if state["steps"] >= MAX_STEPS:

        return "give_up"

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

        return "tools"

    return END


# ---------------------------------------------------------
# GIVE-UP NODE
# ---------------------------------------------------------

def give_up_node(
    state: AgentState,
):

    return {
        "messages": [
            AIMessage(
                content=(
                    "I could not finish this "
                    "within my step limit."
                )
            )
        ]
    }


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
    "tools",
    ToolNode(
        TOOLS
    ),
)


builder.add_node(
    "give_up",
    give_up_node,
)


builder.add_edge(
    START,
    "agent",
)


builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools":
            "tools",

        "give_up":
            "give_up",

        END:
            END,
    },
)


builder.add_edge(
    "tools",
    "agent",
)


builder.add_edge(
    "give_up",
    END,
)


app = builder.compile()


# ---------------------------------------------------------
# TRACE PRINTING
# ---------------------------------------------------------

def print_message_trace(
    messages,
):

    print()
    print(
        "========== AGENT TRACE =========="
    )

    for index, message in enumerate(
        messages,
        start=1,
    ):

        print()
        print(
            f"Message {index}"
        )

        if isinstance(
            message,
            HumanMessage,
        ):

            print(
                "Type: USER"
            )

            print(
                "Content:",
                message.content,
            )

        elif isinstance(
            message,
            ToolMessage,
        ):

            print(
                "Type: OBSERVATION"
            )

            print(
                "Tool:",
                message.name,
            )

            print(
                "Content:",
                message.content,
            )

        elif isinstance(
            message,
            AIMessage,
        ):

            if message.tool_calls:

                print(
                    "Type: TOOL CALL"
                )

                for call in (
                    message.tool_calls
                ):

                    print(
                        "Tool:",
                        call["name"],
                    )

                    print(
                        "Arguments:",
                        call["args"],
                    )

            else:

                print(
                    "Type: ANSWER"
                )

                print(
                    "Content:",
                    message.content,
                )

        else:

            print(
                "Type:",
                type(message).__name__,
            )

            print(
                "Content:",
                message.content,
            )

    print()
    print(
        "================================="
    )


# ---------------------------------------------------------
# TEST RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    question = (
        "Find a science fiction book "
        "and tell me if it is available."
    )

    print()
    print(
        "Week 7 - Part A"
    )

    print(
        "LangGraph Agent Fundamentals"
    )

    print()
    print(
        "User question:"
    )

    print(
        question
    )

    initial_state = {
        "messages": [
            HumanMessage(
                content=question
            )
        ],
        "steps": 0,
    }

    result = app.invoke(
        initial_state,
        config={
            "recursion_limit": 20
        },
    )

    print_message_trace(
        result["messages"]
    )

    print()
    print(
        "Final step count:",
        result["steps"],
    )

    print()
    print(
        "========== MERMAID GRAPH =========="
    )

    print(
        app
        .get_graph()
        .draw_mermaid()
    )

    print(
        "====================================="
    )