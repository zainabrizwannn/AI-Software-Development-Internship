import os
import re
import requests

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import (
    AIMessage,
    HumanMessage
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough
)
from langchain_core.tools import tool

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain_ollama import ChatOllama

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_classic.retrievers.multi_query import (
    MultiQueryRetriever
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
            "Sources used to produce "
            "the answer"
        )
    )


@tool
def check_book_availability(
    book_id: int
) -> str:
    """
    Check whether a specific library book
    is currently available to borrow.
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
            return "Book not found."

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


def get_known_titles():

    titles = []

    if not os.path.exists(
        DOCUMENTS_FOLDER
    ):
        return titles

    for filename in os.listdir(
        DOCUMENTS_FOLDER
    ):

        if not filename.endswith(".txt"):
            continue

        title = os.path.splitext(
            filename
        )[0]

        titles.append(
            title
        )

    return titles


KNOWN_TITLES = get_known_titles()


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
        model="models/gemini-embedding-001",
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


gemini_model = (
    ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0
    )
)


ollama_model = (
    ChatOllama(
        model="llama3.2:3b",
        temperature=0
    )
)


primary_model = (
    gemini_model.with_fallbacks(
        [
            ollama_model
        ]
    )
)


tool_model = (
    ollama_model.bind_tools(
        [
            check_book_availability
        ]
    )
)


multi_query_retriever = (
    MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=ollama_model
    )
)


session_store: dict[
    str,
    list
] = {}


def get_session_history(
    session_id: str
):

    if session_id not in session_store:

        session_store[
            session_id
        ] = []

    return session_store[
        session_id
    ]


def clear_session(
    session_id: str
):

    if session_id in session_store:

        del session_store[
            session_id
        ]


def find_last_book_title(
    history
):

    if not history:
        return None

    for message in reversed(
        history
    ):

        content = str(
            message.content
        ).lower()

        for title in KNOWN_TITLES:

            if (
                title.lower()
                in content
            ):
                return title

    return None


def resolve_follow_up(
    question: str,
    history
) -> str:

    if not history:
        return question

    lowered = (
        question.lower()
    )

    follow_up_patterns = [
        r"\bit\b",
        r"\bthat book\b",
        r"\bthis book\b",
        r"\bthe book\b"
    ]

    is_follow_up = any(
        re.search(
            pattern,
            lowered
        )
        for pattern in follow_up_patterns
    )

    if not is_follow_up:
        return question

    last_title = (
        find_last_book_title(
            history
        )
    )

    if not last_title:
        return question

    resolved = question

    resolved = re.sub(
        r"\bthat book\b",
        last_title,
        resolved,
        flags=re.IGNORECASE
    )

    resolved = re.sub(
        r"\bthis book\b",
        last_title,
        resolved,
        flags=re.IGNORECASE
    )

    resolved = re.sub(
        r"\bthe book\b",
        last_title,
        resolved,
        flags=re.IGNORECASE
    )

    resolved = re.sub(
        r"\bit\b",
        last_title,
        resolved,
        flags=re.IGNORECASE
    )

    print(
        "Memory resolved question:",
        resolved
    )

    return resolved


def history_to_text(
    history
) -> str:

    if not history:
        return ""

    lines = []

    for message in history:

        if message.type == "human":
            role = "User"
        else:
            role = "Assistant"

        lines.append(
            f"{role}: "
            f"{message.content}"
        )

    return "\n".join(
        lines
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

    phrases = [
        "available",
        "availability",
        "borrowed",
        "borrow",
        "checked out",
        "currently available"
    ]

    return any(
        phrase in lowered
        for phrase in phrases
    )


def extract_book_id(
    question: str
):

    cleaned = (
        question
        .replace("?", " ")
        .replace(",", " ")
        .replace(".", " ")
    )

    for word in cleaned.split():

        if word.isdigit():

            return int(
                word
            )

    return None


def retrieve_documents(
    inputs: dict
):

    question = inputs[
        "question"
    ]

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
        multi_query_retriever.invoke(
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

Do not invent information.

If the information is not available,
say that you do not have that information.

Pay attention to the exact book title
mentioned in the current question.

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
    | ollama_model
)


structured_model = (
    ollama_model
    .with_structured_output(
        BookAnswer
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


def content_to_text(
    content
) -> str:

    if isinstance(
        content,
        str
    ):
        return content

    if isinstance(
        content,
        list
    ):

        parts = []

        for item in content:

            if isinstance(
                item,
                str
            ):
                parts.append(
                    item
                )

            elif isinstance(
                item,
                dict
            ):

                text = item.get(
                    "text"
                )

                if text:
                    parts.append(
                        text
                    )

        return "".join(
            parts
        )

    if content is None:
        return ""

    return str(
        content
    )


def run_availability_tool(
    question: str,
    session_id: str
) -> str:

    history = get_session_history(
        session_id
    )

    book_id = extract_book_id(
        question
    )

    if book_id is None:

        answer = (
            "Please provide the book ID "
            "so I can check availability."
        )

    else:

        answer = (
            check_book_availability.invoke(
                {
                    "book_id":
                    book_id
                }
            )
        )

    history.append(
        HumanMessage(
            content=question
        )
    )

    history.append(
        AIMessage(
            content=answer
        )
    )

    return answer


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

    history = get_session_history(
        session_id
    )

    resolved_question = (
        resolve_follow_up(
            question,
            history
        )
    )

    result = text_chain.invoke(
        {
            "question":
                resolved_question,

            "history":
                list(history)
        }
    )

    answer = content_to_text(
        result.content
    )

    history.append(
        HumanMessage(
            content=question
        )
    )

    history.append(
        AIMessage(
            content=answer
        )
    )

    return answer


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
            "parsed":
                parsed,

            "raw":
                AIMessage(
                    content=answer
                )
        }

    history = get_session_history(
        session_id
    )

    resolved_question = (
        resolve_follow_up(
            question,
            history
        )
    )

    try:

        parsed = (
            structured_chain.invoke(
                {
                    "question":
                        resolved_question,

                    "history":
                        list(history)
                }
            )
        )

        answer = parsed.answer

    except Exception:

        result = (
            text_chain.invoke(
                {
                    "question":
                        resolved_question,

                    "history":
                        list(history)
                }
            )
        )

        answer = content_to_text(
            result.content
        )

        parsed = BookAnswer(
            answer=answer,
            confidence="medium",
            sources=[
                "Library RAG documents"
            ]
        )

    history.append(
        HumanMessage(
            content=question
        )
    )

    history.append(
        AIMessage(
            content=answer
        )
    )

    return {
        "parsed":
            parsed,

        "raw":
            AIMessage(
                content=answer
            )
    }


def stream_answer(
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

        yield answer
        return

    history = get_session_history(
        session_id
    )

    resolved_question = (
        resolve_follow_up(
            question,
            history
        )
    )

    result = text_chain.invoke(
        {
            "question":
                resolved_question,

            "history":
                list(history)
        }
    )

    complete_answer = (
        content_to_text(
            result.content
        )
    )

    history.append(
        HumanMessage(
            content=question
        )
    )

    history.append(
        AIMessage(
            content=complete_answer
        )
    )

    words = complete_answer.split()

    for index, word in enumerate(
        words
    ):

        if index < len(words) - 1:
            yield word + " "
        else:
            yield word

    if is_availability_question(
        question
    ):

        answer = (
            run_availability_tool(
                question,
                session_id
            )
        )

        yield answer
        return

    history = get_session_history(
        session_id
    )

    resolved_question = (
        resolve_follow_up(
            question,
            history
        )
    )

    complete_answer = ""

    stream = text_chain.stream(
        {
            "question":
                resolved_question,

            "history":
                list(history)
        }
    )

    for chunk in stream:

        text = content_to_text(
            chunk.content
        )

        if not text:
            continue

        complete_answer += text

        yield text

    history.append(
        HumanMessage(
            content=question
        )
    )

    history.append(
        AIMessage(
            content=complete_answer
        )
    )


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
        documents[
            :n_results
        ]
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


if __name__ == "__main__":

    print(
        "Week 6 Project - "
        "Library AI Assistant"
    )

    print()

    print(
        "Testing availability tool:"
    )

    result = (
        check_book_availability.invoke(
            {
                "book_id": 2
            }
        )
    )

    print(
        result
    )

    print()

    print(
        "Testing session memory:"
    )

    test_session = (
        "final-memory-test"
    )

    first = ask_text(
        "Who wrote The Alchemist?",
        test_session
    )

    print(
        "Q1:",
        first
    )

    second = ask_text(
        "Who wrote it?",
        test_session
    )

    print(
        "Q2:",
        second
    )