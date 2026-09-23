import os
from dotenv import load_dotenv
from google import genai
import chromadb
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Chroma DB
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(
    name="library_rag")

# Chunk Text
def chunk_text(text, chunk_size=150, overlap=30):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Gemini Embeddings
def get_embedding(text):
    response = client.models.embed_content( model="gemini-embedding-001",
        contents=text )
    return response.embeddings[0].values

# Add Document
def add_document(text, source):
    chunks = chunk_text(text)
    embeddings = []
    for chunk in chunks: embeddings.append(get_embedding(chunk))

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=[{
                "source": source,
                "chunk": i }
            for i in range(len(chunks)) ],
        ids=[f"{source}-{i}"
            for i in range(len(chunks)) ])

# Load Documents
def load_documents():

    documents_folder = os.path.join(os.path.dirname(__file__), "documents")
    if collection.count() > 0:
        return
    for file in os.listdir(documents_folder):
        path = os.path.join(documents_folder, file)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            add_document(text, file)

# Retrieve
def retrieve(question, k=3):

    question_embedding = get_embedding(question)
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=k)
    return (
        results["documents"][0],
        results["metadatas"][0])

# Build Prompt
def build_prompt(question, chunks):
    context = "\n\n".join(chunks)
    prompt = f"""

Answer ONLY using the context below.
If the answer is not present in the context, reply exactly:
"I don't have that information."
Context:
{context}
Question:
{question} """
    return prompt