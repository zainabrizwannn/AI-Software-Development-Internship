import time
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


# =========================================================
# CONFIG
# =========================================================

RUNS_PER_SCENARIO = 3


# =========================================================
# TOOLS
# =========================================================

@tool
def search_catalog(query: str) -> str:
    """Search the library catalog."""

    return (
        "Dune: book_id=1, science fiction, available=true. "
        "Foundation: book_id=2, science fiction, available=false. "
        "Clean Code: book_id=3, programming, available=true."
    )


@tool
def check_book_availability(book_id: int) -> str:
    """Check availability for a book."""

    if book_id in [1, 3]:
        return f"Book {book_id} is available."

    return f"Book {book_id} is unavailable."


@tool
def get_my_reservations() -> str:
    """Return current user's reservations only."""

    return "Current user's reservations: book_id=2006."


@tool
def reserve_book(book_id: int) -> str:
    """
    Simulate reservation request.
    Real write requires approval.
    """

    return (
        f"APPROVAL_REQUIRED: reserve_book(book_id={book_id})"
    )


TOOLS = [
    search_catalog,
    check_book_availability,
    get_my_reservations,
    reserve_book,
]


# =========================================================
# MODEL
# =========================================================

model = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    num_predict=80,
    num_ctx=2048,
)

model_with_tools = model.bind_tools(
    TOOLS
)


SYSTEM_PROMPT = """
You are a library assistant.

Use tools only when needed.

Rules:
- search_catalog is for finding books.
- check_book_availability checks availability.
- get_my_reservations accesses only the current user's data.
- reserve_book represents a write request and requires approval.
- never invent private data.
- keep responses short.
"""


# =========================================================
# SCENARIOS
# =========================================================

@dataclass
class Scenario:
    name: str
    prompt: str
    expected_tool: str | None


SCENARIOS = [
    Scenario(
        "Catalog search",
        "Find me a science fiction book.",
        "search_catalog",
    ),

    Scenario(
        "Availability check",
        "Is book 1 available?",
        "check_book_availability",
    ),

    Scenario(
        "Reservation request",
        "Reserve book 1 for me.",
        "reserve_book",
    ),

    Scenario(
        "My reservations",
        "Show my reservations.",
        "get_my_reservations",
    ),

    Scenario(
        "Programming book search",
        "Find me a programming book.",
        "search_catalog",
    ),

    Scenario(
        "Unavailable book check",
        "Is book 2 available?",
        "check_book_availability",
    ),

    Scenario(
        "Reserve another book",
        "Please reserve book 3.",
        "reserve_book",
    ),

    Scenario(
        "General greeting",
        "Hello, how are you?",
        None,
    ),

    Scenario(
        "Book recommendation",
        "Recommend a science fiction title.",
        "search_catalog",
    ),

    Scenario(
        "Current user data",
        "What books have I reserved?",
        "get_my_reservations",
    ),
]


# =========================================================
# RUN ONE SCENARIO
# =========================================================

def run_scenario(
    scenario: Scenario,
    run_number: int,
):
    start = time.perf_counter()

    response = model_with_tools.invoke(
        [
            SystemMessage(
                content=SYSTEM_PROMPT
            ),
            HumanMessage(
                content=scenario.prompt
            ),
        ]
    )

    elapsed = (
        time.perf_counter()
        - start
    )

    tool_names = [
        call["name"]
        for call in response.tool_calls
    ]

    if scenario.expected_tool is None:
        passed = (
            len(tool_names) == 0
        )
    else:
        passed = (
            scenario.expected_tool
            in tool_names
        )

    print(
        f"Run {run_number}: "
        f"{'PASS' if passed else 'FAIL'} "
        f"| tools={tool_names if tool_names else 'NONE'} "
        f"| latency={elapsed:.2f}s"
    )

    return {
        "passed": passed,
        "latency": elapsed,
        "tools": tool_names,
    }


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("WEEK 7 PART G - AGENT EVALUATION")
    print("=" * 70)

    total_runs = 0
    total_passed = 0
    total_latency = 0.0

    scenario_summary = []

    for scenario in SCENARIOS:

        print()
        print(
            f"SCENARIO: {scenario.name}"
        )

        print(
            f"Prompt: {scenario.prompt}"
        )

        print("-" * 70)

        scenario_passes = 0
        scenario_latency = 0.0

        for run_number in range(
            1,
            RUNS_PER_SCENARIO + 1,
        ):

            result = run_scenario(
                scenario,
                run_number,
            )

            total_runs += 1
            total_latency += result[
                "latency"
            ]

            scenario_latency += result[
                "latency"
            ]

            if result["passed"]:
                total_passed += 1
                scenario_passes += 1

        pass_rate = (
            scenario_passes
            / RUNS_PER_SCENARIO
            * 100
        )

        avg_latency = (
            scenario_latency
            / RUNS_PER_SCENARIO
        )

        scenario_summary.append(
            {
                "name":
                    scenario.name,

                "passes":
                    scenario_passes,

                "pass_rate":
                    pass_rate,

                "avg_latency":
                    avg_latency,
            }
        )

    overall_pass_rate = (
        total_passed
        / total_runs
        * 100
    )

    overall_latency = (
        total_latency
        / total_runs
    )

    print()
    print("=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)

    print(
        f"Total runs: {total_runs}"
    )

    print(
        f"Passed runs: {total_passed}"
    )

    print(
        f"Overall pass rate: "
        f"{overall_pass_rate:.1f}%"
    )

    print(
        f"Average latency: "
        f"{overall_latency:.2f}s"
    )

    print()
    print("SCENARIO SUMMARY")
    print("-" * 70)

    for item in scenario_summary:

        print(
            f"{item['name']}: "
            f"{item['passes']}/"
            f"{RUNS_PER_SCENARIO} "
            f"({item['pass_rate']:.1f}%) "
            f"| avg latency="
            f"{item['avg_latency']:.2f}s"
        )