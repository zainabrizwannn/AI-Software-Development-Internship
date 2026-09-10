# Practice Task 1 - Conversation History
import os
import json
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Conversation History Example

history = []
print("Simple Chat (type 'exit' to quit)\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    history.append(f"User: {user_input}")
    prompt = "\n".join(history)
    response = client.models.generate_content( model="gemini-3.6-flash",contents=prompt)

    reply = response.text
    print("AI:", reply)
    history.append(f"AI: {reply}")