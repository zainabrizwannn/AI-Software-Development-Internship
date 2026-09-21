import os
import numpy as np
from dotenv import load_dotenv
from google import genai
# Load environment variables
load_dotenv()
# Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Function to create embeddings
def embed(text):
    response = client.models.embed_content( model="models/gemini-embedding-001",contents=text)
    return response.embeddings[0].values
# Cosine Similarity
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# -------------------------------------------------
# Practice Task 1
# -------------------------------------------------
v1 = embed("A young wizard attends a magic school")
v2 = embed("A boy learns spells at an academy")
v3 = embed("A recipe for chocolate cake")
print("========== TASK 1 ==========")
print("Similar meaning score   :", cosine_similarity(v1, v2))
print("Unrelated meaning score :", cosine_similarity(v1, v3))

# -------------------------------------------------
# Practice Task 2
# -------------------------------------------------
print("\n========== TASK 2 ==========")
print("Embedding Length :", len(v1))
print("First 10 Numbers :", v1[:10])


# -------------------------------------------------
# Practice Task 3
# -------------------------------------------------
v4 = embed("I loved this book")
v5 = embed("I did not love this book")

print("\n========== TASK 3 ==========")
print("Opposite sentence similarity :", cosine_similarity(v4, v5))

print("\nObservation:")
print("- Similar meaning sentences should have a higher similarity score.")
print("- Unrelated sentences should have a much lower similarity score.")
print("- Opposite sentences often remain fairly similar because embeddings capture topic/semantic context more than exact sentiment.")