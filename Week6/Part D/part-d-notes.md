# Week 6 Part D - Tool Calling with LangChain

## Overview

Part D demonstrates how a LangChain chat model can decide whether a live external tool is needed.

The tool used in this task checks the current availability of a book by calling the .NET Library API.

The model is not manually forced to call the function.

Instead, the tool is bound to the model and the model decides whether the user's question requires the tool.

---

## .NET Availability Endpoint

A new public endpoint was added:

`GET /api/Books/{id}/availability`

The Book entity was extended with:

`IsAvailable`

The endpoint returns:

- bookId
- title
- isAvailable

Example response for book 2:

```json
{
  "bookId": 2,
  "title": "The Alchemist",
  "isAvailable": false
}