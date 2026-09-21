import os
from dotenv import load_dotenv
from google import genai
import chromadb
# Load Gemini API
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Chroma DB
chroma_client = chromadb.Client()

collection = chroma_client.create_collection(
    name="library_rag")

# Chunk Function
def chunk_text(text, chunk_size=150, overlap=30):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Gemini Embedding Function
def get_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text )
    return response.embeddings[0].values

# Add Document to Chroma
def add_document(text, source):
    chunks = chunk_text(text)
    embeddings = []
    for chunk in chunks:
        embeddings.append(get_embedding(chunk))
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=[{
                "source": source,
                "chunk": i }
            for i in range(len(chunks))],
        ids=[
            f"{source}-{i}"
            for i in range(len(chunks))] )

# Retrieve Relevant Chunks
def retrieve(question, k=3):
    question_embedding = get_embedding(question)
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=k )

    return results

# Build Prompt
def build_prompt(question, chunks):

    context = "\n\n".join(chunks)

    prompt = f"""
Answer ONLY from the context below.
If the answer is not present in the context, reply:
"I don't have that information."
Context:
{context}
Question:
{question}
"""
    return prompt

# Generate Final Answer
def generate_answer(prompt):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt )
    return response.text

# Load Documents
documents_folder = "documents"

for file in os.listdir(documents_folder):
    path = os.path.join(documents_folder, file)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
        add_document(text, file)
print("Documents loaded successfully!")

# =====================================================
# TASK 1
# =====================================================
print("\n==============================")
print("TASK 1")
print("==============================")

question = "What is Artificial Intelligence used for?"
results = retrieve(question)
chunks = results["documents"][0]
metadata = results["metadatas"][0]

prompt = build_prompt(question, chunks)

answer = generate_answer(prompt)

print("\nQuestion:")
print(question)
print("\nAnswer:")
print(answer)

# =====================================================
# TASK 2
# =====================================================

print("\n==============================")
print("TASK 2")
print("==============================")

question = "Who won the FIFA World Cup in 2022?"

results = retrieve(question)

chunks = results["documents"][0]

prompt = build_prompt(question, chunks)

answer = generate_answer(prompt)
print("\nQuestion:")
print(question)
print("\nAnswer:")
print(answer)

# =====================================================
# TASK 3
# =====================================================

print("\n==============================")
print("TASK 3")
print("==============================")
print("\nRetrieved Sources:\n")

for meta in metadata:
    print(meta)