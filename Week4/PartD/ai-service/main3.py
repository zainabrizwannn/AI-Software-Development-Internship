import os
import json
from dotenv import load_dotenv
from google import genai
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

title = "Atomic Habits"
description = """A practical guide explaining how small daily habits lead to remarkable 
improvements over time."""

prompt = f"""Return ONLY valid JSON in this exact format:
{{
    "genre": "string",
    "summary": "one paragraph" }}
Book Title: {title}
Description: {description} """
response = client.models.generate_content( model="gemini-3.6-flash", contents=prompt )

try:
    data = json.loads(response.text)
    print("Genre:", data["genre"])
    print("\nSummary:")
    print(data["summary"])
except json.JSONDecodeError:
    print("Invalid JSON received.")
    print(response.text)