import httpx


DOTNET_URL = "http://localhost:5194"


def load_preferences(
    token: str,
) -> list[dict]:

    response = httpx.get(
        f"{DOTNET_URL}/api/me/preferences",
        headers={
            "Authorization":
                f"Bearer {token}"
        },
        timeout=8,
    )

    response.raise_for_status()

    return response.json()


def build_system_prompt(
    preferences: list[dict],
) -> str:

    if not preferences:
        return (
            "You are a library assistant. "
            "No long-term preferences are saved."
        )

    preference_text = ", ".join(
        f"{item['key']}={item['value']}"
        for item in preferences
    )

    return (
        "You are a library assistant. "
        "The current user's saved long-term "
        f"preferences are: {preference_text}."
    )


if __name__ == "__main__":

    token = input(
        "Paste JWT: "
    ).strip()

    preferences = load_preferences(
        token
    )

    print()
    print(
        "NEW THREAD"
    )

    print(
        "Loaded preferences:",
        preferences,
    )

    print()
    print(
        "SYSTEM PROMPT"
    )

    print(
        build_system_prompt(
            preferences
        )
    )