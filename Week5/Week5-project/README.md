# Week 5 Project – Library Knowledge Assistant

## Overview

This project extends the FastAPI AI service into a Retrieval-Augmented Generation (RAG) system that answers questions about the library's actual book catalog.

The application retrieves books from the .NET Library API, converts them into text documents, generates embeddings, stores them in ChromaDB, and uses Gemini to answer user questions with source attribution.

---

## Features

- Fetch books from the .NET Library API
- Build a text corpus from the book catalog
- Chunk documents into smaller sections
- Generate embeddings using Gemini
- Store embeddings in ChromaDB
- Retrieve relevant information
- RAG-powered `/ask` endpoint
- Source attribution for every answer
- Grounded responses that avoid hallucinations

---

## Technologies

- Python
- FastAPI
- Google Gemini API
- ChromaDB
- .NET Web API
- Swagger

---

## Project Structure

```
Week5-project/
│
├── backend/
│   └── LibraryAPI2
│
├── ai-services/
│   ├── main.py
│   ├── rag.py
│   ├── fetch_books.py
│   ├── documents/
│   ├── chroma_db/
│   ├── requirements.txt
│   └── .env
│
└── README.md
```

---

## Data Flow

```
SQL Server
      │
      ▼
.NET Library API
(GET /api/books)
      │
      ▼
fetch_books.py
      │
      ▼
documents/
      │
      ▼
rag.py
      │
      ▼
Chunking
      │
      ▼
Gemini Embeddings
      │
      ▼
ChromaDB
      │
      ▼
POST /ask
      │
      ▼
Retrieve Context
      │
      ▼
Gemini
      │
      ▼
Answer + Sources
```

---

## API Endpoints

### GET /

Returns a welcome message.

### POST /summarize

Summarizes supplied text using Gemini.

### POST /ask

Answers questions using Retrieval-Augmented Generation (RAG).

---

## Example

Question:

```
Who wrote Harry Potter?
```

Response:

```json
{
  "answer": "Harry Potter was written by J.K. Rowling.",
  "sources": [
    "Harry Potter.txt"
  ]
}
```