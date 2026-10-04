import os
import requests

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough
)
from langchain_core.runnables.history import (
    RunnableWithMessageHistory
)
from langchain_core.tools import tool
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)
from langchain_classic.retrievers.multi_query import (
    MultiQueryRetriever
)
from langchain_community.chat_message_histories import (
    ChatMessageHistory
)


load_dotenv()


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DOCUMENTS_FOLDER = os.path.join(
    BASE_DIR,
    "documents"
)

CHROMA_FOLDER = os.path.join(
    BASE_DIR,
    "chroma_db"
)

COLLECTION_NAME = (
    "week6_final_library_rag"
)

LIBRARY_API_BASE_URL = (
    "http://localhost:5194"
)


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )


os.environ["GOOGLE_API_KEY"] = (
    GEMINI_API_KEY
)


class BookAnswer(BaseModel):

    answer: str = Field(
        description=(
            "The answer to the user's "
            "library question"
        )
    )

    confidence: str = Field(
        description=(
            "Confidence level: "
            "high, medium, or low"
        )
    )

    sources: list[str] = Field(
        description=(
            "Source documents or services "
            "used for the answer"
        )
    )


@tool
def check_book_availability(
    book_id: int
) -> str:
    """
    Check whether a specific library book
    is currently available to borrow.

    Use this tool only when the user asks
    about current book availability.
    """

    url = (
        f"{LIBRARY_API_BASE_URL}"
        f"/api/Books/"
        f"{book_id}/availability"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code == 404:

            return (
                "Book not found."
            )

        if response.status_code != 200:

            return (
                "Could not check book "
                "availability right now."
            )

        data = response.json()

        title = data.get(
            "title",
            "Unknown book"
        )

        is_available = data.get(
            "isAvailable",
            False
        )

        if is_available:

            return (
                f"{title} is currently "
                "available to borrow."
            )

        return (
            f"{title} is currently "
            "borrowed."
        )

    except requests.RequestException:

        return (
            "Could not connect to the "
            "library availability API."
        )


def load_documents() -> list[Document]:

    documents = []

    if not os.path.exists(
        DOCUMENTS_FOLDER
    ):

        raise FileNotFoundError(
            f"Documents folder not found: "
            f"{DOCUMENTS_FOLDER}"
        )

    for filename in os.listdir(
        DOCUMENTS_FOLDER
    ):

        if not filename.endswith(".txt"):
            continue

        path = os.path.join(
            DOCUMENTS_FOLDER,
            filename
        )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": filename
                }
            )
        )

    return documents


splitter = (
    RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )
)


embeddings = (
    GoogleGenerativeAIEmbeddings(
        model=(
            "models/"
            "gemini-embedding-001"
        ),
        google_api_key=GEMINI_API_KEY
    )
)


vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_FOLDER
)


def ensure_documents_indexed():

    current_count = (
        vectorstore
        ._collection
        .count()
    )

    if current_count > 0:
        return

    documents = load_documents()

    chunks = (
        splitter.split_documents(
            documents
        )
    )

    if not chunks:

        raise ValueError(
            "No document chunks were created."
        )

    vectorstore.add_documents(
        chunks
    )

    print(
        "Week 6 final RAG documents "
        "indexed successfully."
    )


ensure_documents_indexed()


base_retriever = (
    vectorstore.as_retriever(
        search_kwargs={
            "k": 3
        }
    )
)


model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)


model_with_tools = (
    model.bind_tools(
        [
            check_book_availability
        ]
    )
)


multi_query_retriever = (
    MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=model
    )
)


def guard_short_questions(
    inputs: dict
) -> dict:

    question = (
        inputs["question"]
        .strip()
    )

    if len(question) < 3:

        raise ValueError(
            "Question too short to "
            "answer meaningfully."
        )

    return inputs


def is_availability_question(
    question: str
) -> bool:

    lowered = question.lower()

    availability_phrases = [
        "available",
        "availability",
        "borrowed",
        "borrow",
        "checked out",
        "currently available"
    ]

    return any(
        phrase in lowered
        for phrase in availability_phrases
    )


def history_to_text(
    history
) -> str:

    if not history:
        return ""

    lines = []

    for message in history:

        role = (
            "User"
            if message.type == "human"
            else "Assistant"
        )

        lines.append(
            f"{role}: "
            f"{message.content}"
        )

    return "\n".join(
        lines
    )


def retrieve_documents(
    inputs: dict
):

    question = (
        inputs["question"]
    )

    history = inputs.get(
        "history",
        []
    )

    history_text = (
        history_to_text(
            history
        )
    )

    if history_text:

        retrieval_question = (
            "Previous conversation:\n"
            f"{history_text}\n\n"
            "Current question:\n"
            f"{question}"
        )

    else:

        retrieval_question = (
            question
        )

    return (
        multi_query_retriever
        .invoke(
            retrieval_question
        )
    )


def format_documents(
    documents
) -> str:

    formatted = []

    for document in documents:

        source = (
            document.metadata.get(
                "source",
                "Unknown"
            )
        )

        formatted.append(
            f"Source: {source}\n"
            f"{document.page_content}"
        )

    return "\n\n".join(
        formatted
    )


def retrieve_context(
    inputs: dict
) -> str:

    documents = (
        retrieve_documents(
            inputs
        )
    )

    return (
        format_documents(
            documents
        )
    )


prompt = (
    ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a helpful AI library assistant.

Answer using ONLY the retrieved library
context and previous conversation.

If the answer cannot be determined from
the retrieved context or conversation,
say that you do not have that information.

Do not invent book details or sources.

Use previous conversation when the user
asks follow-up questions such as
"Who wrote it?" or "What genre is it?"

Retrieved library context:

{context}
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
)


guard = RunnableLambda(
    guard_short_questions
)


context_runnable = (
    RunnableLambda(
        retrieve_context
    )
)


question_runnable = (
    RunnablePassthrough()
    | RunnableLambda(
        lambda inputs:
        inputs["question"]
    )
)


history_runnable = (
    RunnablePassthrough()
    | RunnableLambda(
        lambda inputs:
        inputs.get(
            "history",
            []
        )
    )
)


structured_model = (
    model.with_structured_output(
        BookAnswer,
        include_raw=True
    )
)


structured_chain = (
    guard
    | {
        "context":
        context_runnable,

        "question":
        question_runnable,

        "history":
        history_runnable
    }
    | prompt
    | structured_model
)


text_chain = (
    guard
    | {
        "context":
        context_runnable,

        "question":
        question_runnable,

        "history":
        history_runnable
    }
    | prompt
    | model
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


structured_chain_with_memory = (
    RunnableWithMessageHistory(
        structured_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
        output_messages_key="raw"
    )
)


text_chain_with_memory = (
    RunnableWithMessageHistory(
        text_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history"
    )
)


def run_availability_tool(
    question: str,
    session_id: str
) -> str:

    history = get_session_history(
        session_id
    )

    system_message = SystemMessage(
        content="""
You are a library assistant.

The user is asking about CURRENT book
availability.

Use the check_book_availability tool when
a book ID is available.

Never invent availability information.

If the user has not provided enough
information to identify a book ID, ask
them to provide the book ID.
"""
    )

    messages = [
        system_message,
        *history.messages,
        HumanMessage(
            content=question
        )
    ]

    first_response = (
        model_with_tools.invoke(
            messages
        )
    )

    if not first_response.tool_calls:

        answer = (
            first_response.content
        )

        history.add_user_message(
            question
        )

        history.add_ai_message(
            answer
        )

        return answer

    tool_messages = []

    for call in (
        first_response.tool_calls
    ):

        if (
            call["name"]
            == "check_book_availability"
        ):

            tool_result = (
                check_book_availability
                .invoke(
                    call["args"]
                )
            )

        else:

            tool_result = (
                "Unknown tool requested."
            )

        tool_messages.append(
            ToolMessage(
                content=tool_result,
                tool_call_id=(
                    call["id"]
                )
            )
        )

    final_messages = [
        *messages,
        first_response,
        *tool_messages
    ]

    final_response = (
        model_with_tools.invoke(
            final_messages
        )
    )

    answer = (
        final_response.content
    )

    history.add_user_message(
        question
    )

    history.add_ai_message(
        answer
    )

    return answer


def stream_availability_tool(
    question: str,
    session_id: str
):

    history = get_session_history(
        session_id
    )

    system_message = SystemMessage(
        content="""
You are a library assistant.

The user is asking about CURRENT book
availability.

Use the check_book_availability tool when
a book ID is available.

Never invent availability information.

If the user has not supplied enough
information to identify a book ID, ask
them for the book ID.
"""
    )

    messages = [
        system_message,
        *history.messages,
        HumanMessage(
            content=question
        )
    ]

    first_response = (
        model_with_tools.invoke(
            messages
        )
    )

    if not first_response.tool_calls:

        answer = (
            first_response.content
        )

        history.add_user_message(
            question
        )

        history.add_ai_message(
            answer
        )

        if answer:
            yield answer

        return

    tool_messages = []

    for call in (
        first_response.tool_calls
    ):

        if (
            call["name"]
            == "check_book_availability"
        ):

            tool_result = (
                check_book_availability
                .invoke(
                    call["args"]
                )
            )

        else:

            tool_result = (
                "Unknown tool requested."
            )

        tool_messages.append(
            ToolMessage(
                content=tool_result,
                tool_call_id=(
                    call["id"]
                )
            )
        )

    final_messages = [
        *messages,
        first_response,
        *tool_messages
    ]

    complete_answer = ""

    for chunk in (
        model_with_tools.stream(
            final_messages
        )
    ):

        text = chunk.content

        if not text:
            continue

        complete_answer += text

        yield text

    history.add_user_message(
        question
    )

    history.add_ai_message(
        complete_answer
    )


def ask_structured(
    question: str,
    session_id: str
):

    if is_availability_question(
        question
    ):

        answer = (
            run_availability_tool(
                question,
                session_id
            )
        )

        parsed = BookAnswer(
            answer=answer,
            confidence="high",
            sources=[
                "Library availability API"
            ]
        )

        return {
            "parsed": parsed,
            "raw": AIMessage(
                content=answer
            )
        }

    return (
        structured_chain_with_memory
        .invoke(
            {
                "question": question
            },
            config={
                "configurable": {
                    "session_id":
                    session_id
                }
            }
        )
    )


def ask_text(
    question: str,
    session_id: str
) -> str:

    if is_availability_question(
        question
    ):

        return (
            run_availability_tool(
                question,
                session_id
            )
        )

    result = (
        text_chain_with_memory
        .invoke(
            {
                "question": question
            },
            config={
                "configurable": {
                    "session_id":
                    session_id
                }
            }
        )
    )

    return result.content


def stream_answer(
    question: str,
    session_id: str
):

    if is_availability_question(
        question
    ):

        yield from (
            stream_availability_tool(
                question,
                session_id
            )
        )

        return

    stream = (
        text_chain_with_memory
        .stream(
            {
                "question": question
            },
            config={
                "configurable": {
                    "session_id":
                    session_id
                }
            }
        )
    )

    for chunk in stream:

        text = (
            chunk.content
        )

        if text:
            yield text


def retrieve(
    question: str,
    n_results: int = 3
):

    documents = (
        multi_query_retriever.invoke(
            question
        )
    )

    documents = (
        documents[:n_results]
    )

    text_documents = [
        document.page_content
        for document in documents
    ]

    metadata = [
        document.metadata
        for document in documents
    ]

    return (
        text_documents,
        metadata
    )


def clear_session(
    session_id: str
):

    if session_id in session_store:

        del session_store[
            session_id
        ]


if __name__ == "__main__":

    print(
        "Week 6 Project - "
        "Library AI Assistant"
    )

    print()

    print(
        "Testing availability tool "
        "without the LLM:"
    )

    result = (
        check_book_availability.invoke(
            {
                "book_id": 2
            }
        )
    )

    print(result)