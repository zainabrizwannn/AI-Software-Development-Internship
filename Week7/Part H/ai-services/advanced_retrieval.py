import logging
import os

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)
from langchain_classic.retrievers.multi_query import MultiQueryRetriever


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY was not found in .env")
DOCUMENTS_FOLDER = "documents"
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s")
logging.getLogger(
    "langchain_classic.retrievers.multi_query"
).setLevel(logging.INFO)

def load_documents():
    documents = []
    for filename in os.listdir(DOCUMENTS_FOLDER):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(DOCUMENTS_FOLDER,filename)
        with open(
            path,
            "r",
            encoding="utf-8") as file:
            text = file.read()
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": filename }))
    return documents


def print_results(title, documents):
    print()
    print(title)
    print("-" * 60)
    if not documents:
        print("No results found.")
        return
    for index, document in enumerate(
        documents,
        start=1
    ):
        source = document.metadata.get(
            "source",
            "Unknown")
        preview = (
            document.page_content
            .replace("\n", " ")
            [:200] )
        print(
            f"{index}. Source: {source}"
        )
        print(
            f"   {preview}")
def get_sources(documents):

    return {
        document.metadata.get(
            "source",
            "Unknown"
        )
        for document in documents
    }


def compare_retrievers(
    question,
    plain_retriever,
    multi_retriever ):
    print()
    print("=" * 70)
    print("QUESTION:")
    print(question)
    print("=" * 70)
    plain_results = plain_retriever.invoke(
        question)
    multi_results = multi_retriever.invoke(
        question)
    print_results(
        "PLAIN RETRIEVER RESULTS",
        plain_results)
    print_results(
        "MULTIQUERY RETRIEVER RESULTS",
        multi_results)
    plain_sources = get_sources(
        plain_results )
    multi_sources = get_sources(
        multi_results )
    extra_sources = (
        multi_sources
        - plain_sources)

    missing_sources = (
        plain_sources
        - multi_sources)
    print()
    print("COMPARISON")
    print("-" * 60)
    print(
        "Plain Retriever:",
        sorted(plain_sources)
    )
    print(
        "MultiQuery Retriever:",
        sorted(multi_sources))
    if extra_sources:
        print(
            "Extra sources from MultiQuery:",
            sorted(extra_sources))
    else:
        print(
            "No extra sources from MultiQuery."
        )

    if missing_sources:

        print(
            "Sources only found by Plain Retriever:",
            sorted(missing_sources))
    return (
        plain_results,
        multi_results)
def main():

    print(
        "Week 6 Part B - Advanced Retrieval" )
    print()
    print("Loading Week 5 documents...")
    documents = load_documents()

    print(
        "Documents loaded:",
        len(documents))
    splitter = (
        RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""])
    )

    chunks = splitter.split_documents(
        documents
    )

    print(
        "Chunks created:",
        len(chunks)
    )

    embeddings = (
        GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=GEMINI_API_KEY
        )
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="week6_part_b_retrieval"
    )

    plain_retriever = (
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

    multi_retriever = (
        MultiQueryRetriever.from_llm(
            retriever=plain_retriever,
            llm=model
        )
    )
    test_questions = [
        "Which book is about data structures and algorithms?",
        "Who wrote Harry Potter?",
        "Which book is related to software engineering?",
        "Which books are available in the library?",
        "Which book should I read if I want to learn programming?"]
    print()
    print("#" * 70)
    print(
        "CHALLENGE 1 - FIVE QUESTION RETRIEVAL COMPARISON")
    print("#" * 70)
    for number, question in enumerate(
        test_questions,
        start=1 ):
        print()
        print(
            f"TEST QUESTION {number}")
        compare_retrievers(
            question,
            plain_retriever,
            multi_retriever)
    print()
    print("#" * 70)
    print(
        "CHALLENGE 2 - MULTIQUERY PRECISION TRADE-OFF"
    )
    print("#" * 70)

    worse_question = (
        "I specifically want the book about "
        "data structures and algorithms. "
        "Which book matches that topic?"
    )
    compare_retrievers(
        worse_question,
        plain_retriever,
        multi_retriever
    )
    print()
    print("=" * 70)
    print(
        "PART B EXECUTION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()