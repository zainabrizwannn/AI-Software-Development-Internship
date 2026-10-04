# Week 6 Project — Library AI Assistant

This project connects the Angular frontend, .NET backend, FastAPI AI service, LangChain RAG pipeline, tool calling, session memory, and resilient streaming into one working Library AI Assistant.

## Project Architecture

The application uses the following flow:

Angular Chat UI
→ .NET Library API
→ FastAPI AI Service
→ LangChain RAG Pipeline
→ LLM / Tool
→ Streamed response back through FastAPI
→ .NET
→ Angular UI

## Full Data Flow

1. The user enters a question in the Angular chat interface.

2. Angular sends the request to:

   POST /api/Assistant/ask/stream

3. The .NET backend forwards the request to the FastAPI AI service.

4. The .NET backend includes resilience handling such as:

   - Retry policy
   - Timeout policy
   - Circuit breaker
   - Clear temporary-unavailable responses

5. FastAPI receives the request at:

   POST /ask/stream

6. FastAPI passes the question and session ID to the LangChain pipeline.

7. The LangChain RAG pipeline includes:

   - LCEL composition
   - RecursiveCharacterTextSplitter
   - Chroma vector store
   - MultiQueryRetriever
   - Structured output
   - Session-scoped memory
   - Availability tool integration

8. For normal library questions, relevant documents are retrieved from the vector database and passed to the LLM.

9. The current local runtime uses Ollama with the llama3.2:3b model for reliable local generation and streaming.

10. Gemini remains configured in the project, but local Ollama is used for the main runtime path to avoid external quota interruptions.

11. For availability questions such as:

   "Is book 2 available right now?"

   the LangChain availability tool calls:

   GET /api/Books/{id}/availability

   on the .NET backend.

12. The answer is returned through FastAPI and .NET to the Angular chat interface.

## Main Features

### LangChain RAG

The RAG pipeline combines the concepts developed in Week 6 Parts A–C.

It includes:

- LCEL composition
- RecursiveCharacterTextSplitter
- Chroma vector database
- MultiQueryRetriever
- Structured response models
- Session-scoped conversation memory

### Availability Tool

The assistant can check real book availability from the .NET database.

Example:

User:

Is book 2 available right now?

Assistant:

The Alchemist is currently borrowed.

### Session Memory

Each Angular browser chat session uses a session ID.

The session ID flows through:

Angular
→ .NET
→ FastAPI
→ LangChain memory

This allows follow-up questions to use previous conversation context.

Example:

User:

Who wrote The Alchemist?

Assistant:

The author of "The Alchemist" is Robert C. Martin.

User:

Who wrote it?

Assistant:

Robert C. Martin wrote "The Alchemist".

### Streaming

Responses are returned through the streaming endpoint:

POST /api/Assistant/ask/stream

The response is passed through:

FastAPI
→ .NET streaming proxy
→ Angular chat UI

The Angular interface displays the answer progressively.

### Resilience

The .NET AI client includes:

- Retry handling
- Timeout handling
- Circuit breaker
- HTTP failure handling

If the AI service is stopped or unavailable, the UI shows a clear message instead of hanging or crashing.

Example:

The AI assistant is temporarily unavailable. Please try again shortly.

## Technologies Used

### Frontend

- Angular
- TypeScript
- HTML
- CSS

### Backend

- ASP.NET Core
- Entity Framework Core
- SQL Server
- Polly
- JWT Authentication

### AI Service

- Python
- FastAPI
- LangChain
- Chroma
- Ollama
- Gemini integration

### Local Model

- Ollama
- llama3.2:3b

## Important Endpoints

### .NET

POST /api/Assistant/ask

POST /api/Assistant/ask/stream

GET /api/Books/{id}/availability

### FastAPI

POST /ask

POST /ask/text

POST /ask/stream

POST /session/clear

GET /health

## Resilience Test

The FastAPI service was intentionally stopped while Angular and .NET remained running.

The Angular UI returned a clear temporary-unavailable state rather than hanging or crashing.

## Memory Test

A multi-turn conversation was tested using the same session.

Example:

Who wrote The Alchemist?

followed by:

Who wrote it?

The assistant correctly resolved the follow-up question using the previous conversation.

## Availability Test

The availability tool was tested against the .NET endpoint.

Example result:

The Alchemist is currently borrowed.

## Known Limitations

- Session memory is stored only in memory.
- Session history is lost when the FastAPI process restarts.
- Conversation history is not persisted to a database.
- Ollama must be installed and running locally for the local model path.
- Gemini API generation can be affected by free-tier quota limits.
- The project uses a simple in-memory session store and is not designed for distributed deployment.
- The current project does not implement a full multi-step autonomous agent. That work is reserved for Week 7.

## Week 6 Milestone

This project integrates the main Week 6 features into one complete workflow:

Angular
→ .NET
→ FastAPI
→ LangChain RAG
→ retrieval / memory / tool
→ LLM
→ streamed response
→ Angular
## Final Status

Week 6 integration completed successfully with RAG, availability lookup, resilience, streaming, and session memory.