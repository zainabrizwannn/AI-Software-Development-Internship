import os
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Sample book data
book_title = "Atomic Habits"

book_description = """
A practical guide that explains how small daily habits can lead to remarkable personal and professional improvements over time.
"""

prompt = f"""
Book Title: {book_title}

Book Description:
{book_description}

Generate a one-paragraph summary of this book and suggest the most suitable genre.
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

print(response.text)