import os
import requests

from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY was not found in .env")


API_BASE_URL = "http://localhost:5194"


@tool
def check_book_availability(book_id: int) -> str:
    """
    Check whether a specific book is currently available to borrow.
    Use this tool only when the user asks about current book availability.
    """
    url = (
        f"{API_BASE_URL}/api/Books/"
        f"{book_id}/availability" )
    try:
        response = requests.get(
            url,
            timeout=10)
        if response.status_code == 404:
            return "Book not found."
        if response.status_code != 200:
            return "Could not check availability right now."
        data = response.json()
        if data["isAvailable"]:
            return (
                f'{data["title"]} is currently available.' )
        return (
            f'{data["title"]} is currently borrowed.')
    except requests.RequestException:
        return "Could not connect to the library API."

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=GEMINI_API_KEY )
model_with_tools = model.bind_tools(
    [check_book_availability]
)

def run_tool_calling(question: str):
    print()
    print("=" * 70)
    print("QUESTION:")
    print(question)
    print("=" * 70)
    first_response = model_with_tools.invoke([
            HumanMessage(
                content=question )])

    if not first_response.tool_calls:
        print()
        print("MODEL DECISION:")
        print("No tool call needed.")
        print()
        print("MODEL ANSWER:")
        print(first_response.content)
        return
    print()
    print("MODEL DECISION:")
    print("Tool call requested.")

    messages = [
        HumanMessage(
            content=question ),
        first_response ]
    for call in first_response.tool_calls:
        print()
        print("TOOL NAME:")
        print(call["name"])
        print("TOOL ARGUMENTS:")
        print(call["args"])
        tool_result = (
            check_book_availability.invoke(
                call["args"] ))

        print()
        print("RAW TOOL RESULT:")
        print(tool_result)
        messages.append(
            ToolMessage(
                content=tool_result,
                tool_call_id=call["id"] ))

    final_response = model_with_tools.invoke(
        messages )
    print()
    print("FINAL NATURAL LANGUAGE ANSWER:")
    print(final_response.content)
if __name__ == "__main__":
    print(
        "Week 6 Part D - Tool Calling" )
    run_tool_calling(
        "Is book 2 available right now?")

    run_tool_calling(
        "What genre is book 2?")