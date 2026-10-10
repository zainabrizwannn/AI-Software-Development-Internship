import time

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama


model = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


if __name__ == "__main__":

    question = (
        "Find me an available sci-fi book "
        "and reserve it."
    )

    print()
    print("=" * 70)
    print("PART E - SINGLE AGENT MEASUREMENT")
    print("=" * 70)

    start_time = time.perf_counter()

    response = model.invoke(
        [
            HumanMessage(
                content=question
            )
        ]
    )

    end_time = time.perf_counter()

    elapsed = (
        end_time - start_time
    )

    print()
    print(
        "Model calls:",
        1,
    )

    print(
        f"Elapsed time: "
        f"{elapsed:.2f} seconds"
    )

    print()
    print(
        "Response:"
    )

    print(
        response.content
    )