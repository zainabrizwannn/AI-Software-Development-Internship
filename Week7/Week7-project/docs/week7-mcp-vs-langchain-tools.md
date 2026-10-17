# Week 7 — MCP vs LangChain Tools

## Introduction

Model Context Protocol, or MCP, is an open protocol for exposing tools, data and prompts from a server to compatible AI clients.

In the current library-assistant project, tools such as `search_catalog`, `check_book_availability`, and `reserve_book` are implemented directly inside the Python/LangChain codebase. This works well for one application, but the tools are tightly connected to that application.

MCP would change this design by allowing the library capabilities to be exposed from an MCP server and then discovered and used by different compatible AI clients.

---

## Current LangChain Tool Design

In the current implementation, tools are defined inside the agent code.

Examples include:

- `search_catalog`
- `check_book_availability`
- `reserve_book`
- `get_my_reservations`

The LangGraph agent knows about these tools because they are imported and registered directly in the Python application.

This approach has several advantages:

- simple to understand
- easy to debug in one codebase
- tool schemas are close to the agent logic
- no additional tool server is required

However, it also means the tools are mainly reusable only inside applications that import or recreate the same Python code.

---

## What MCP Would Change

With MCP, the library tools could be moved behind a dedicated MCP server.

For example, the MCP server could expose:

- `search_catalog`
- `check_book_availability`
- `reserve_book`

Instead of defining these tools separately in every AI application, compatible clients could discover the available capabilities through the MCP protocol.

The library tool implementation would therefore become more independent from a specific LangChain or LangGraph application.

The agent would still need authorization and approval controls, but tool discovery and invocation would use a standard protocol.

---

## Reuse

One of the main benefits of MCP is reuse.

The same MCP library server could potentially be used by:

- the current LangGraph assistant
- another desktop AI client
- a different orchestration framework
- an internal developer tool
- another future library application

The tool implementation would not need to be rewritten for every client.

With normal LangChain tools, the tool definitions are usually written as part of the application itself, so reuse often requires importing or copying application-specific code.

---

## Standard Discovery

MCP also provides a standard way for a client to discover what tools and resources a server provides.

This is useful because the client does not need every tool to be manually hard-coded into the same project.

For the library system, an MCP client could discover capabilities such as catalog search and reservation from the MCP server.

This can make integration easier when multiple applications need access to the same AI-facing capabilities.

---

## Security and Trust Boundary

MCP also introduces another trust boundary.

In the current LangChain design, the tool implementation is inside the same application and can be reviewed together with the agent.

With MCP, the client may connect to another server that provides tools.

This creates additional security questions:

- Who operates the MCP server?
- Can the server be trusted?
- What data is sent to it?
- Which tools are read-only and which can modify data?
- How is the user authenticated?
- Can the server expose unexpected or malicious tools?
- Can third-party servers return untrusted content?

For the `reserve_book` tool, this is especially important because it changes persistent state.

The same controls used in the current project would still be required:

- server-side authorization
- ownership checks
- argument validation
- idempotency
- approval before writes
- rate limits
- audit logging

MCP standardizes how tools are exposed, but it does not remove the need for application security.

---

## MCP vs LangChain Tools

| Area | LangChain Tools | MCP |
|---|---|---|
| Definition | Usually defined inside application code | Exposed by an MCP server |
| Reuse | Mainly within the same application or Python codebase | Can be reused across compatible clients |
| Discovery | Tools are normally registered manually | Standard tool discovery |
| Complexity | Lower for a small application | Adds another protocol and server boundary |
| Security | Mostly controlled inside one application | Requires trust in the MCP server as well |
| Best use | Small or tightly controlled applications | Shared capabilities across multiple AI clients |

---

## Recommendation for the Library Assistant

For the current library assistant, LangChain tools are simpler and sufficient because the system is still relatively small and the tools are closely connected to one application.

If the same catalog and circulation tools later need to be shared across multiple AI applications, MCP would become attractive because the tools could be implemented once and exposed through a standard interface.

I would therefore keep the current LangChain tool implementation for the present project, while considering MCP if the library capabilities become shared infrastructure across multiple clients.