import os
from operator import itemgetter

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_chroma import Chroma
from langchain_core.documents import Document
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

COLLECTION_NAME = "week6_final_library_rag"


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
            "Source document names used "
            "to answer the question"
        )
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


splitter = RecursiveCharacterTextSplitter(
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
        vectorstore._collection.count()
    )

    if current_count > 0:
        return

    documents = load_documents()

    chunks = splitter.split_documents(
        documents
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
            f"{role}: {message.content}"
        )

    return "\n".join(lines)


def retrieve_documents(
    inputs: dict
):

    question = inputs["question"]

    history = inputs.get(
        "history",
        []
    )

    history_text = history_to_text(
        history
    )

    if history_text:

        retrieval_question = (
            "Previous conversation:\n"
            f"{history_text}\n\n"
            "Current question:\n"
            f"{question}"
        )

    else:

        retrieval_question = question

    documents = (
        multi_query_retriever.invoke(
            retrieval_question
        )
    )

    return documents


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

    documents = retrieve_documents(
        inputs
    )

    return format_documents(
        documents
    )


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a helpful AI library assistant.

Answer using ONLY the retrieved library
context and the previous conversation.

If the answer cannot be determined from
the retrieved context or conversation,
reply that you do not have that information.

Do not invent book details or sources.

Use previous conversation messages when
the user asks a follow-up question such as
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


guard = RunnableLambda(
    guard_short_questions
)


context_runnable = RunnableLambda(
    retrieve_context
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
        "context": context_runnable,
        "question": question_runnable,
        "history": history_runnable
    }
    | prompt
    | structured_model
)


text_chain = (
    guard
    | {
        "context": context_runnable,
        "question": question_runnable,
        "history": history_runnable
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


def ask_structured(
    question: str,
    session_id: str
):

    result = (
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

    return result


def ask_text(
    question: str,
    session_id: str
) -> str:

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

        text = chunk.content

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

    documents = documents[
        :n_results
    ]

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
        "Combined LangChain RAG Chain"
    )

    print()

    session_id = "week6-test-user"

    first_question = (
        "Tell me about one of the "
        "books in the library."
    )

    print("QUESTION 1:")
    print(first_question)

    first_answer = ask_text(
        first_question,
        session_id
    )

    print()
    print("ANSWER 1:")
    print(first_answer)

    print()

    second_question = (
        "What category is it?"
    )

    print("QUESTION 2:")
    print(second_question)

    second_answer = ask_text(
        second_question,
        session_id
    )

    print()
    print("ANSWER 2:")
    print(second_answer)