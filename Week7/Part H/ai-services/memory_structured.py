import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.runnables.history import (
    RunnableWithMessageHistory
)
from langchain_community.chat_message_histories import (
    ChatMessageHistory
)


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )


class BookAnswer(BaseModel):
    answer: str = Field(
        description="The answer to the user's question"
    )

    confidence: str = Field(
        description="'high', 'medium', or 'low'"
    )

    sources: list[str] = Field(
        description="Book titles the answer was drawn from"
    )


model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GEMINI_API_KEY
)


structured_model = model.with_structured_output(
    BookAnswer,
    include_raw=True
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a helpful library assistant.

Answer the user's questions about books.

Use the previous conversation when the user
asks a follow-up question.

Return a structured answer containing:

- answer
- confidence
- sources

If the question cannot be answered from the
conversation or supplied information, clearly
say that there is not enough context.

Do not invent sources.
"""
        ),

        MessagesPlaceholder(
            variable_name="history"
        ),

        (
            "human",
            "{question}"
        )
    ]
)


chain = (
    prompt
    | structured_model
)


session_store: dict[
    str,
    ChatMessageHistory
] = {}


def get_session_history(
    session_id: str
) -> ChatMessageHistory:

    if session_id not in session_store:

        session_store[
            session_id
        ] = ChatMessageHistory()

    return session_store[
        session_id
    ]


chain_with_memory = (
    RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
        output_messages_key="raw"
    )
)


def ask_question(
    question: str,
    session_id: str
):
    result = chain_with_memory.invoke(
        {
            "question": question
        },
        config={
            "configurable": {
                "session_id": session_id
            }
        }
    )

    return result


def display_result(result):

    parsed = result["parsed"]

    print()
    print("Structured Output")
    print("-" * 60)

    print(
        "Answer:",
        parsed.answer
    )

    print(
        "Confidence:",
        parsed.confidence
    )

    print(
        "Sources:",
        parsed.sources
    )

    print()
    print(
        "Returned Python type:",
        type(parsed).__name__
    )


if __name__ == "__main__":

    print(
        "Week 6 Part C - Challenge 2")
    print()
    print(
        "STRUCTURED OUTPUT + MEMORY")
    print("=" * 60)
    session_id = "challenge-2-user"

    print()
    print(
        "FIRST QUESTION")
    print("-" * 60)
    first_result = ask_question(
        (
            "Tell me about Dune. "
            "Dune is a science fiction novel "
            "written by Frank Herbert."
        ),
        session_id    )
    display_result(
        first_result    )

    print()
    print(
        "FOLLOW-UP QUESTION USING MEMORY" )
    print("-" * 60)

    follow_up_result = ask_question(
        "Who wrote it and what genre is it?",
        session_id
    )

    display_result(
        follow_up_result)
    print()
    print(
        "STRUCTURED OUTPUT TYPE CHECK" )
    print("-" * 60)
    parsed_result = (
        follow_up_result["parsed"] )
    print(
        "Answer type:",
        type(parsed_result.answer).__name__)
    print(
        "Confidence type:",
        type(parsed_result.confidence).__name__)
    print(
        "Sources type:",
        type(parsed_result.sources).__name__)
    print(
        "Full object type:",
        type(parsed_result).__name__)
    print()
    print(
        "CHALLENGE 2 COMPLETE"
    )