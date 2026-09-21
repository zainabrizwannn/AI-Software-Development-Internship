import os
from dotenv import load_dotenv
from google import genai
import chromadb
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def embed(text):
    response = client.models.embed_content( model="gemini-embedding-001",contents=text)
    return response.embeddings[0].values

# Create Chroma client
chroma_client = chromadb.Client()
# Delete collection if it already exists
try:
    chroma_client.delete_collection("books_demo")
except: pass

collection = chroma_client.create_collection(name="books_demo",embedding_function=None)
documents = [
    "A young wizard attends a magic school and fights a dark lord.",
    "A crew travels through a wormhole to save humanity from a dying Earth.",
    "Two feuding families in nineteenth century England navigate love and marriage.",
    "Artificial intelligence is changing software development.",
    "Python is one of the most popular programming languages."]

metadatas = [
    {"source": "book1.txt", "category": "Fantasy"},
    {"source": "book2.txt", "category": "Science Fiction"},
    {"source": "book3.txt", "category": "Romance"},
    {"source": "book4.txt", "category": "Technology"},
    {"source": "book5.txt", "category": "Programming"}]

ids = [
    "book1",
    "book2",
    "book3",
    "book4",
    "book5"]
embeddings = [embed(doc) for doc in documents]
collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

print("========== TASK 1 ==========")
query_embedding = embed("a space journey story")
results = collection.query( query_embeddings=[query_embedding], n_results=2)
print(results["documents"])
print(results["metadatas"])

print("\n========== TASK 2 ==========")
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=2,
    where={"category": "Fantasy"})
print(results["documents"])
print(results["metadatas"])


print("\n========== TASK 3 ==========")
query_embedding = embed("machine learning")
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3)
print(results["documents"])
print(results["metadatas"])