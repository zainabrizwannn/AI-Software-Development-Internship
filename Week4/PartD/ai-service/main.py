# Practice Task 2 - Temperature Comparison
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = "Invent a unique fantasy book title and write a one-paragraph plot about a dragon who wants to become a librarian."
print("Temperature = 0")
response1 = client.models.generate_content( model="gemini-3.6-flash", contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0
    ))
print(response1.text)

print("\nTemperature = 1")
response2 = client.models.generate_content(
    model="gemini-3.6-flash", contents=prompt,
    config=types.GenerateContentConfig(
        temperature=1
    ))
print(response2.text)