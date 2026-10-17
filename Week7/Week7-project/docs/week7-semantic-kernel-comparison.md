# Week 7 — Semantic Kernel vs LangGraph Comparison

## Introduction

The current library assistant uses Python with LangGraph for agent orchestration.

An alternative would be to move the orchestration into the .NET backend and use Microsoft's Semantic Kernel.

Semantic Kernel is designed for building AI applications in C# and other supported languages using plugins, functions and automatic function calling.

Because the rest of the library backend is already implemented in .NET, this alternative could simplify some parts of the architecture.

---

## Current LangGraph Architecture

The current system uses:

- .NET for authentication, database access and secure APIs
- Python for LangGraph orchestration
- LangChain tools for agent actions
- FastAPI as the AI-service boundary
- Angular for the user interface

LangGraph manages:

- agent state
- routing
- retries
- tool execution
- human approval
- checkpointing
- resume behavior

This gives the project a strong agent-oriented workflow model, but it also means the system has both a .NET backend and a Python AI service.

---

## What Would Become Easier with Semantic Kernel

If orchestration moved into the .NET backend, several parts could become easier.

### One Main Backend Technology

The system could use C# for both business logic and AI orchestration.

This would reduce the need to maintain a separate Python FastAPI service.

The current communication path:

`.NET -> FastAPI -> agent`

could potentially become:

`.NET -> Semantic Kernel`

This would reduce one network boundary.

### Direct Access to Existing Services

The backend already contains:

- EF Core
- JWT authentication
- reservation logic
- ownership checks
- user preferences
- rate limiting

Semantic Kernel plugins could call existing C# services directly.

For example, a circulation plugin could call the reservation service without requiring an HTTP call back into the .NET API.

### Shared Models and Validation

C# models, dependency injection and validation could be reused directly.

This could make argument validation and authorization easier to integrate with existing backend code.

### Easier Deployment

A single .NET deployment could be simpler than deploying both:

- ASP.NET Core
- FastAPI/Python

This would also reduce operational complexity.

---

## What Could Become Harder

Moving to Semantic Kernel would also have disadvantages.

### Agent Workflow Migration

The current LangGraph implementation already includes:

- explicit graph nodes
- conditional edges
- retry paths
- approval interrupts
- checkpoint persistence
- resumable runs

These concepts would need to be rebuilt or mapped into Semantic Kernel patterns.

### Different Ecosystem

The current project already uses LangChain and LangGraph tools and examples.

Moving frameworks would require learning a different orchestration model and rewriting some of the Python agent code.

### Checkpointing and Long-Running State

LangGraph is particularly strong at representing stateful workflows as graphs.

The current project uses checkpointing and thread IDs to pause and resume runs.

A Semantic Kernel implementation would need an equivalent persistence strategy for:

- pending approvals
- agent state
- retries
- resumed workflows

Some of this may need to be implemented at the application level.

---

## What Would Be Lost

The biggest loss would be access to the existing Python/LangChain/LangGraph ecosystem already used by this project.

The current implementation benefits from:

- LangGraph state graphs
- LangChain tools
- Python AI libraries
- local Ollama integrations
- existing agent examples and utilities

Moving orchestration entirely into .NET would mean replacing or reimplementing parts that already work.

It could also make experimentation with new Python-first AI libraries less convenient.

---

## Security Comparison

Both approaches still require the same important security controls.

Neither LangGraph nor Semantic Kernel should be treated as the security boundary.

The system still needs:

- server-side authorization
- least-privilege tools
- approval before write actions
- validated arguments
- rate limits
- idempotency
- ownership checks
- safe secret handling

Semantic Kernel could make some of these easier to connect directly to the .NET backend, but the controls themselves would still be required.

---

## Comparison

| Area | Python + LangGraph | .NET + Semantic Kernel |
|---|---|---|
| Workflow graphs | Strong explicit graph model | Different orchestration model |
| Existing project work | Already implemented | Requires migration |
| .NET integration | Requires HTTP/service boundary | Native |
| EF Core access | Through backend APIs | Direct |
| Deployment | .NET + Python services | Potentially one .NET service |
| AI ecosystem | Very large Python ecosystem | Strong Microsoft/.NET integration |
| Checkpointing | Built into current LangGraph approach | May require more application design |
| Developer stack | Mixed Python and C# | Mostly C# |

---

## Recommendation

For the current project, I would keep LangGraph for the existing implementation.

The project already has working routing, retries, human approval, checkpointing and persistence in LangGraph. Rewriting these features in Semantic Kernel during the current development cycle would add risk without providing enough immediate benefit.

However, if this library system were redesigned from the beginning as a primarily .NET product, Semantic Kernel would be a strong option because it could keep orchestration, authentication, database access and business logic in the same technology stack.

Therefore, my recommendation is:

- keep LangGraph for the current project
- consider Semantic Kernel for future .NET-first systems where reducing Python/.NET integration complexity is a major goal