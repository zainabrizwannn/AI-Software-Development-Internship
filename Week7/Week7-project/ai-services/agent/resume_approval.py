from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from hitl_workflow import (
    CHECKPOINT_DB,
    builder,
    print_messages,
)


if __name__ == "__main__":

    thread_id = "u1002:part-d-demo"

    config = {
        "configurable": {
            "thread_id": thread_id,

            # Still kept in config,
            # never in graph state.
            "user_token": "DEMO_TOKEN_NOT_STORED_IN_STATE",
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
            "PART D - RESUME APPROVAL"
        )

        print(
            "Thread ID:",
            thread_id,
        )

        print()
        print(
            "Resuming paused graph "
            "with APPROVED = TRUE..."
        )

        result = app.invoke(
            Command(
                resume={
                    "approved": True
                }
            ),
            config,
        )

        print()
        print(
            "Graph resumed successfully."
        )

        print_messages(
            result["messages"]
        )

        print()
        print(
            "Final steps:",
            result["steps"],
        )

        print(
            "Final retries:",
            result["retries"],
        )