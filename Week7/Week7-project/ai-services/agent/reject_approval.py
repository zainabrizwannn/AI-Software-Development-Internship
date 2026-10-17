from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from hitl_workflow import (
    CHECKPOINT_DB,
    builder,
    print_messages,
)


if __name__ == "__main__":

    thread_id = (
        "u1002:part-d-reject-demo"
    )

    config = {
        "configurable": {
            "thread_id":
                thread_id,
        }
    }

    with SqliteSaver.from_conn_string(
        CHECKPOINT_DB
    ) as saver:

        app = builder.compile(
            checkpointer=saver
        )

        print()
        print(
            "Starting rejection test..."
        )

        first_result = app.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            "Reserve book 2005 "
                            "for me."
                        )
                    )
                ],
                "steps": 0,
                "retries": 0,
            },
            config,
        )

        print()
        print(
            "Graph paused for approval."
        )

        print(
            "Interrupt:",
            first_result.get(
                "__interrupt__"
            ),
        )

        print()
        print(
            "Resuming with APPROVED = FALSE..."
        )

        final_result = app.invoke(
            Command(
                resume={
                    "approved": False
                }
            ),
            config,
        )

        print_messages(
            final_result["messages"]
        )

        print()
        print(
            "Final steps:",
            final_result["steps"],
        )