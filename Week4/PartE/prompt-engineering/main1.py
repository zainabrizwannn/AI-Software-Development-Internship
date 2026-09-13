import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

book_title = "Atomic Habits"
book_description = ( "A practical guide that explains how small daily habits can lead "
 "to remarkable personal and professional improvements over time.")

# Zero-shot Prompt
zero_shot = f""" Suggest a genre for this book and give a one-paragraph summary.
Book Title: {book_title}
Description: {book_description} """
response = client.models.generate_content( model="gemini-3.6-flash", contents=zero_shot )
print("===== ZERO-SHOT =====")
print(response.text)

# Few-shot Prompt
few_shot = f""" Classify the genre.
Examples:
Book: Dune
Description: A desert planet, political intrigue.
Genre: Science Fiction

Book: Pride and Prejudice
Description: Manners and marriage in 19th century England.
Genre: Romance

Now classify this book.

Book: {book_title}
Description: {book_description}
Also provide a one-paragraph summary."""
response = client.models.generate_content( model="gemini-3.6-flash", contents=few_shot)
print("\n==== FEW-SHOT =====")
print(response.text)

# Role Prompt
role_prompt = f""" You are a professional library cataloguer.
Reply in this format only:

Genre:
Summary:
Book Title: {book_title}
Description: {book_description}"""
response = client.models.generate_content( model="gemini-3.6-flash", contents=role_prompt)
print("\n===== ROLE PROMPT =====")
print(response.text)