from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel


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
# ROUTER PROMPT
# ---------------------------------------------------------

ROUTER_PROMPT = """
You are a routing classifier for a library assistant.

Your job is to classify the user's message into exactly one route.

Available routes:

1. catalog
Use this for:
- questions about books
- finding books
- authors
- genres
- categories
- availability
- book information
- recommendations based on the library catalog

2. action
Use this when the user wants the system to change data or perform an action, such as:
- reserve a book
- cancel a reservation
- create or modify something
- perform a write operation

3. chitchat
Use this for:
- greetings
- thanks
- casual conversation
- small talk
- messages unrelated to the library catalog or actions

Important:
Return only one of:
catalog
action
chitchat
"""


# ---------------------------------------------------------
# MODEL
# ---------------------------------------------------------

model = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


router = model.with_structured_output(
    Route
)


# ---------------------------------------------------------
# ROUTER FUNCTION
# ---------------------------------------------------------

def classify_message(
    message: str,
) -> str:

    result = router.invoke(
        [
            SystemMessage(
                content=ROUTER_PROMPT
            ),
            HumanMessage(
                content=message
            ),
        ]
    )

    return result.route


# ---------------------------------------------------------
# TEST SET
# ---------------------------------------------------------

TEST_MESSAGES = [
    # -------------------------
    # CATALOG
    # -------------------------

    (
        "Find me a book about software engineering.",
        "catalog",
    ),

    (
        "Is book 2006 available?",
        "catalog",
    ),

    (
        "Who wrote Clean Code?",
        "catalog",
    ),

    (
        "Show me books by Robert C. Martin.",
        "catalog",
    ),

    (
        "Do you have any science fiction books?",
        "catalog",
    ),

    # -------------------------
    # ACTION
    # -------------------------

    (
        "Reserve book 2005 for me.",
        "action",
    ),

    (
        "I want to reserve DSA.",
        "action",
    ),

    (
        "Please reserve book 1010.",
        "action",
    ),

    (
        "Cancel my reservation for book 2006.",
        "action",
    ),

    (
        "Reserve this book now.",
        "action",
    ),

    # -------------------------
    # CHITCHAT
    # -------------------------

    (
        "Hello!",
        "chitchat",
    ),

    (
        "Thanks for your help.",
        "chitchat",
    ),

    (
        "How are you?",
        "chitchat",
    ),

    (
        "Good morning.",
        "chitchat",
    ),

    (
        "Tell me a joke.",
        "chitchat",
    ),
  (
    "What do you think about Dune?",
    "catalog",
),
]


# ---------------------------------------------------------
# TEST RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    total = len(
        TEST_MESSAGES
    )

    correct = 0

    print()
    print(
        "=" * 70
    )

    print(
        "WEEK 7 - PART C ROUTER TEST"
    )

    print(
        "=" * 70
    )

    for index, (
        message,
        expected,
    ) in enumerate(
        TEST_MESSAGES,
        start=1,
    ):

        predicted = classify_message(
            message
        )

        is_correct = (
            predicted == expected
        )

        if is_correct:
            correct += 1

        print()
        print(
            f"Test {index}"
        )

        print(
            "Message:",
            message,
        )

        print(
            "Expected:",
            expected,
        )

        print(
            "Predicted:",
            predicted,
        )

        print(
            "Result:",
            "PASS"
            if is_correct
            else "MISS",
        )

    accuracy = (
        correct / total
    ) * 100

    print()
    print(
        "=" * 70
    )

    print(
        f"Correct: {correct}/{total}"
    )

    print(
        f"Accuracy: {accuracy:.2f}%"
    )

    print(
        "=" * 70
    )
   