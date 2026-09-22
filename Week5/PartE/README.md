## Testing

### Tested Endpoints

### GET /

Returns a welcome message.

### POST /summarize

Generates the genre and summary for a book.

### POST /ask

Accepts a question, retrieves relevant document chunks using ChromaDB, generates an answer with Gemini, and returns the answer along with the source document(s).

Example:

Question:
What is Artificial Intelligence used for?

Response:
{
  "answer": ""answer": "AI is widely used in healthcare, finance, education, and software development.",
  "sources": [
    "ai.txt",
    "python.txt""
  ]
}