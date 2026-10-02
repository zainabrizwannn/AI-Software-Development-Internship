# Week 6 Part C - Structured Output and Conversation Memory

## Overview

Part C focuses on two LangChain features:

1. Structured output using Pydantic models
2. Session-scoped conversation memory using RunnableWithMessageHistory

The implementation uses Gemini through LangChain.

---

## Structured Output

A Pydantic model called `BookAnswer` was created.

It contains three fields:

- `answer`
- `confidence`
- `sources`

The model is attached to the Gemini chat model using:

`with_structured_output(BookAnswer)`

This means the model response is returned as a typed Python object instead of manually asking the model to generate JSON and then parsing it.

Example structured result:

- Answer: Information about Dune
- Confidence: high
- Sources: Dune

Returned Python type:

`BookAnswer`

This confirms that structured output is working correctly.

---

## Why Structured Output Is Better Than Manual JSON

In a manual JSON approach, the model is only instructed to return valid JSON.

This can fail if the model:

- adds extra text
- produces invalid JSON
- misses required fields
- returns unexpected field types

Using `with_structured_output()` binds the expected Pydantic schema directly to the model.

This provides more reliable and predictable output.

---

# Challenge 1 - Session-Scoped Conversation Memory

The purpose of Challenge 1 was to verify that conversation history is maintained separately for each session.

A Python dictionary is used as the session store.

Each conversation is identified by a unique `session_id`.

The function:

`get_session_history(session_id)`

returns the message history associated with that session.

---

## Session A

Session ID:

`user-42`

First question:

`Tell me about the book Dune. It is a science fiction novel written by Frank Herbert.`

The structured result identified Dune correctly.

Output fields included:

- Answer: Information about Dune
- Confidence: high
- Sources: Dune
- Python object type: BookAnswer

---

## Same-Session Follow-Up

The same session then asked:

`What genre is it?`

The question did not repeat the name `Dune`.

Because the same session ID `user-42` was used, the previous conversation history was available.

The model correctly understood that `it` referred to Dune and answered that Dune is a science fiction novel.

This confirms that conversation memory works across messages within the same session.

---

## Fresh Session

A separate session ID was created:

`user-99`

The same follow-up question can be sent using this new session:

`What genre is it?`

Because this session has its own independent history, it does not contain the previous discussion about Dune.

This demonstrates the purpose of session-scoped memory:

- one user's history is not shared with another user
- every session maintains its own conversation context

---

# Challenge 2 - Structured Output and Memory Together

The second challenge combines both features in the same LCEL chain.

The structured model is created first:

`model.with_structured_output(BookAnswer)`

It is then used inside the prompt chain.

The complete chain is wrapped using:

`RunnableWithMessageHistory`

This allows the same chain to provide:

- conversation memory
- typed structured output

at the same time.

---

## Challenge 2 Test Design

A session called:

`challenge-2-user`

is used.

First question:

`Tell me about Dune. Dune is a science fiction novel written by Frank Herbert.`

Follow-up question:

`Who wrote it and what genre is it?`

The follow-up does not repeat the title Dune.

Conversation memory allows the chain to understand that `it` refers to Dune.

At the same time, the answer is returned using the `BookAnswer` schema.

The expected structured fields are:

- `answer`
- `confidence`
- `sources`

The expected Python types are:

- answer → `str`
- confidence → `str`
- sources → `list`
- complete result → `BookAnswer`

This demonstrates how structured output and session-scoped memory can be composed in the same LangChain pipeline.

---

# Session Storage

The current implementation uses an in-memory Python dictionary:

`session_store`

Example:

`session_store: dict[str, ChatMessageHistory] = {}`

Each session ID has its own `ChatMessageHistory`.

---

## In-Memory Limitation

The current session store is temporary.

If the Python or FastAPI process restarts, all conversation history stored in the dictionary is lost.

This is acceptable for the Week 6 internship exercise.

A production system should use persistent storage such as:

- Redis
- SQL database
- NoSQL database

Persistent storage would allow conversation history to survive application restarts and support multiple application instances.

---

# Part C Result

Part C demonstrates:

- Pydantic-based structured responses
- `with_structured_output()`
- typed `BookAnswer` objects
- session-scoped conversation history
- `RunnableWithMessageHistory`
- same-session follow-up questions
- separate histories for different session IDs
- structured output and conversation memory composed in the same chain
- understanding of the limitation of temporary in-memory storage