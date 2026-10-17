from pathlib import Path

from langchain_core.messages import (
    HumanMessage,
)
from langgraph.checkpoint.sqlite import (
    SqliteSaver,
)
from langgraph.types import (
    Command,
)

from main_workflow import (
    builder,
)


# =========================================================
# CHECKPOINT LOCATION
# =========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

CHECKPOINT_DB = (
    BASE_DIR
    / "agent_checkpoints.sqlite"
)


# =========================================================
# INITIAL STATE
# =========================================================

def initial_state(
    message: str,
) -> dict:

    return {
        "messages": [
            HumanMessage(
                content=message
            )
        ],

        "route":
            "",

        "steps":
            0,

        "retries":
            0,

        "selected_book_id":
            None,

        "tool_result":
            "",

        "final_answer":
            "",
    }


# =========================================================
# CONFIG
# =========================================================

def runtime_config(
    thread_id: str,
    user_token: str,
) -> dict:

    return {
        "configurable": {
            "thread_id":
                thread_id,

            # SECURITY:
            # JWT is runtime config only.
            # It is not part of AgentState and therefore
            # should not be persisted into checkpoints.
            "user_token":
                user_token,

            # One stable key for this agent thread.
            # reserve_book appends the book ID.
            "idempotency_key":
                f"agent:{thread_id}",
        }
    }


# =========================================================
# START
# =========================================================

def start_persistent_run(
    thread_id: str,
    message: str,
    user_token: str,
) -> dict:

    config = runtime_config(
        thread_id,
        user_token,
    )

    with (
        SqliteSaver
        .from_conn_string(
            str(
                CHECKPOINT_DB
            )
        )
    ) as saver:

        app = builder.compile(
            checkpointer=saver
        )

        result = app.invoke(
            initial_state(
                message
            ),
            config=config,
        )

        return result


# =========================================================
# RESUME
# =========================================================

def resume_persistent_run(
    thread_id: str,
    approved: bool,
    user_token: str,
) -> dict:

    config = runtime_config(
        thread_id,
        user_token,
    )

    with (
        SqliteSaver
        .from_conn_string(
            str(
                CHECKPOINT_DB
            )
        )
    ) as saver:

        app = builder.compile(
            checkpointer=saver
        )

        result = app.invoke(
            Command(
                resume={
                    "approved":
                        approved
                }
            ),
            config=config,
        )

        return result


# =========================================================
# READ CURRENT STATE
# =========================================================

def get_persistent_state(
    thread_id: str,
    user_token: str,
):

    config = runtime_config(
        thread_id,
        user_token,
    )

    with (
        SqliteSaver
        .from_conn_string(
            str(
                CHECKPOINT_DB
            )
        )
    ) as saver:

        app = builder.compile(
            checkpointer=saver
        )

        return app.get_state(
            config
        )


# =========================================================
# SECURITY CHECK
# =========================================================

def checkpoint_contains_token(
    user_token: str,
) -> bool:
    """
    Verify that the JWT has not been written
    into the SQLite checkpoint file.
    """

    if not CHECKPOINT_DB.exists():
        return False

    data = CHECKPOINT_DB.read_bytes()

    token_bytes = (
        user_token.encode(
            "utf-8"
        )
    )

    return (
        token_bytes
        in data
    )