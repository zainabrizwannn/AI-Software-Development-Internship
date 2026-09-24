import os
import chromadb
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Chroma Client
chroma_client = chromadb.PersistentClient(path="chroma_db")

DOCUMENTS_FOLDER = "documents"
COLLECTION_NAME = "library_books"


def chunk_text(text, chunk_size=150, overlap=30):
    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap

    return chunks


def get_embedding(text):
    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values


def get_collection():
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )

def index_documents():

    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except:
        pass
    collection = get_collection()
    chunk_id = 0
    for filename in os.listdir(DOCUMENTS_FOLDER):

        if not filename.endswith(".txt"):
            continue
        path = os.path.join(DOCUMENTS_FOLDER, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        title = "Unknown"
        category = "Unknown"
        for line in text.splitlines():
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()

            elif line.startswith("Category:"):
                category = line.replace("Category:", "").strip()

        chunks = chunk_text(text)

        for chunk in chunks:

            embedding = get_embedding(chunk)

            collection.add(
                ids=[str(chunk_id)],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "title": title,
                    "category": category,
                    "source": filename
                }]
            )

            chunk_id += 1

    print("Documents indexed successfully!")


def retrieve(question, n_results=3):

    collection = get_collection()

    embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )

    documents = results["documents"][0]
    metadata = results["metadatas"][0]

    return documents, metadata


if __name__ == "__main__":
    index_documents()