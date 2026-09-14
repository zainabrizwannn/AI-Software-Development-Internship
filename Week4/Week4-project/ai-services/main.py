from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-3.6-flash")

app = FastAPI(title="Library AI Service")


# Request model
class BookRequest(BaseModel):
    title: str
    description: str


@app.get("/")
def home():
    return {"message": "AI Service Running"}


@app.post("/summarize")
def summarize(book: BookRequest):
    prompt = f"""
You are a librarian and book expert.

Analyze the following book.

Title:
{book.title}

Description:
{book.description}

Return ONLY valid JSON in this exact format:

{{
    "genre": "Genre name",
    "summary": "A concise one-paragraph summary."
}}

Do not include markdown.
Do not include explanation.
Do not wrap the JSON in ``` blocks.
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Remove markdown code fences if Gemini adds them
        text = text.replace("```json", "").replace("```", "").strip()

        result = json.loads(text)

        return result

    except json.JSONDecodeError:
        return {
            "error": "Unable to parse AI response."
        }

    except Exception as e:
        return {
            "error": str(e)
        }