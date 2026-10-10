from langchain_core.tools import StructuredTool
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# TOOL ARGUMENT SCHEMAS
# ---------------------------------------------------------

class AvailabilityArgs(BaseModel):
    book_id: int = Field(
        gt=0,
        description="Numeric ID of the library book",
    )


class SearchArgs(BaseModel):
    query: str = Field(
        min_length=1,
        description="Title, author, category, or search phrase",
    )


# ---------------------------------------------------------
# TOOL FUNCTIONS
# ---------------------------------------------------------

def check_availability_function(
    book_id: int,
) -> str:
    return (
        f"Availability check requested "
        f"for book ID {book_id}."
    )


def search_catalog_function(
    query: str,
) -> str:
    return (
        f"Catalog search requested "
        f"for: {query}"
    )


# ---------------------------------------------------------
# THREE DESCRIPTION VERSIONS
# ---------------------------------------------------------

VAGUE_DESCRIPTION = """
Check a book.
"""


PRECISE_DESCRIPTION = """
Check whether a specific library book is currently available.

Use this tool when the user asks whether a known book can
currently be borrowed or reserved.

The tool requires the numeric book ID.

Do not use this tool when the user only wants to search,
browse, or discover books.
"""


OVER_LONG_DESCRIPTION = """
This tool is related to library books and can be used in
situations involving books, availability, borrowing,
reservations, lending, checking whether something exists,
checking whether something can potentially be borrowed,
looking at the current status of an item, or when the user
mentions a book and appears to need information about that
book.

The tool accepts a numeric book ID and returns information
about whether the corresponding book is currently available.
It may be useful when the user asks about borrowing,
reserving, availability, library status, current book status,
whether a book can be obtained now, whether a particular
book is present, or other related library questions.

Do not use invalid book IDs. Consider the overall user
question before choosing this tool. If another tool seems
more appropriate, use that tool instead. This tool does not
perform a general catalog search, although some user
questions may mention books, titles, authors, genres,
categories, availability, reservations, or borrowing at the
same time.
"""


# ---------------------------------------------------------
# SEARCH TOOL
# ---------------------------------------------------------

search_catalog = StructuredTool.from_function(
    func=search_catalog_function,
    name="search_catalog",
    description=(
        "Search the library catalog by title, author, "
        "category, or topic. Use this when the user wants "
        "to find or discover books."
    ),
    args_schema=SearchArgs,
)


# ---------------------------------------------------------
# MODEL
# ---------------------------------------------------------

model = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


# ---------------------------------------------------------
# TEST QUESTIONS
# ---------------------------------------------------------

QUESTIONS = [
    "Is book 2006 available?",
    "Can I borrow book 3 right now?",
    "Find me a book about software engineering.",
    "What books are in the catalog?",
    "Can book 1010 be reserved right now?",
]


# ---------------------------------------------------------
# EXPERIMENT
# ---------------------------------------------------------

def run_experiment(
    label: str,
    availability_description: str,
):
    check_book_availability = (
        StructuredTool.from_function(
            func=check_availability_function,
            name="check_book_availability",
            description=availability_description,
            args_schema=AvailabilityArgs,
        )
    )

    tools = [
        check_book_availability,
        search_catalog,
    ]

    model_with_tools = model.bind_tools(
        tools
    )

    print()
    print("=" * 70)
    print(label)
    print("=" * 70)

    for number, question in enumerate(
        QUESTIONS,
        start=1,
    ):
        reply = model_with_tools.invoke(
            question
        )

        print()
        print(
            f"Question {number}: "
            f"{question}"
        )

        if reply.tool_calls:
            for call in reply.tool_calls:
                print(
                    "Tool selected:",
                    call["name"],
                )

                print(
                    "Arguments:",
                    call["args"],
                )
        else:
            print(
                "Tool selected: NO TOOL"
            )

            print(
                "Model response:",
                reply.content,
            )


# ---------------------------------------------------------
# RUN ALL THREE VERSIONS
# ---------------------------------------------------------

if __name__ == "__main__":
    run_experiment(
        "VERSION 1 - VAGUE DESCRIPTION",
        VAGUE_DESCRIPTION,
    )

    run_experiment(
        "VERSION 2 - PRECISE DESCRIPTION",
        PRECISE_DESCRIPTION,
    )

    run_experiment(
        "VERSION 3 - OVER-LONG DESCRIPTION",
        OVER_LONG_DESCRIPTION,
    )