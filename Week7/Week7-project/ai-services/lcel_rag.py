import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough
)

from rag import retrieve
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")

os.environ["GOOGLE_API_KEY"] = gemini_api_key
model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0
)
prompt = ChatPromptTemplate.from_template(
    """You are a helpful AI library assistant.
Answer ONLY using the context below.
If the answer is not contained in the context, reply exactly:
I don't have that information.
Context:
{context}
Question:
{question}
Answer:
""")
def guard_short_questions(inputs: dict) -> dict:
    question = inputs["question"].strip()

    if len(question) < 3:
        raise ValueError(
            "Question too short to answer meaningfully."
        )

    return inputs


def retrieve_context(inputs: dict) -> str:
    documents, metadata = retrieve(
        inputs["question"])
    return "\n\n".join(documents)
guard = RunnableLambda(
    guard_short_questions
)
context_runnable = RunnableLambda(
    retrieve_context
)
question_runnable = (
    RunnablePassthrough()
    | RunnableLambda(
        lambda inputs: inputs["question"]
    )
)
chain = (
    guard
    | {
        "context": context_runnable,
        "question": question_runnable
    }
    | prompt
    | model
    | StrOutputParser()
)
if __name__ == "__main__":

    print("Week 6 Part A - LCEL RAG")
    print()

    question = "Which books are available in the library?"
    print("Question:")
    print(question)
    print()
    answer = chain.invoke(
        {
            "question": question})

    print("Answer:")
    print(answer)