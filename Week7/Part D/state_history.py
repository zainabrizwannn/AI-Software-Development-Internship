from langgraph.checkpoint.sqlite import SqliteSaver

from hitl_workflow import (
    CHECKPOINT_DB,
    builder,
)


if __name__ == "__main__":

    thread_id = "u1002:part-d-demo"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    with SqliteSaver.from_conn_string(
        CHECKPOINT_DB
    ) as saver:

        app = builder.compile(
            checkpointer=saver
        )

        print()
        print("=" * 70)
        print("PART D - STATE HISTORY")
        print("=" * 70)

        history = list(
            app.get_state_history(
                config
            )
        )

        print(
            "Checkpoint count:",
            len(history),
        )

        for index, snapshot in enumerate(
            history,
            start=1,
        ):
            print()
            print("-" * 70)
            print(
                f"Checkpoint {index}"
            )

            print(
                "Next:",
                snapshot.next,
            )

            values = snapshot.values

            print(
                "Steps:",
                values.get(
                    "steps"
                ),
            )

            print(
                "Retries:",
                values.get(
                    "retries"
                ),
            )

            print(
                "Message count:",
                len(
                    values.get(
                        "messages",
                        [],
                    )
                ),
            )

            print(
                "Metadata:",
                snapshot.metadata,
            )