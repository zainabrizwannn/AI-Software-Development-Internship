# Week 7 — Testing, Evaluation & Tracing Report

## Objective

The purpose of Part G was to separate deterministic software testing from non-deterministic agent evaluation.

Deterministic components were tested using pytest and xUnit. Model-driven behavior was evaluated using repeated scenarios and measured using pass rate, tool trajectory and latency.

---

## Python Deterministic Tests

The Python test suite covered:

- retryable errors
- conflict handling
- final errors
- successful tool results
- negative book IDs
- zero book IDs
- HTTP 409 mapping
- HTTP 404 mapping
- HTTP 401 mapping

Result:

- Total tests: 9
- Passed: 9
- Failed: 0

These tests do not require a real LLM and verify deterministic agent logic.

---

## .NET Integration Tests

The .NET xUnit test suite covered:

- reservation endpoint requires authentication
- current-user reservations require authentication
- preferences require authentication
- unknown book returns 404
- unavailable book returns 409
- repeated reservation with the same idempotency key creates one reservation
- cross-user thread access is rejected

Result:

- Total tests: 7
- Passed: 7
- Failed: 0

The tests use an SQLite in-memory relational database and a deterministic test-authentication handler.

---

## Agent Evaluation

The model-based evaluation used 10 fixed scenarios.

Each scenario was run 3 times, producing 30 total runs.

Scenarios included:

1. Catalog search
2. Availability check
3. Reservation request
4. Current-user reservations
5. Programming-book search
6. Unavailable-book check
7. Another reservation request
8. General greeting
9. Book recommendation
10. Current-user data request

Measured results:

- Total runs: REPLACE_TOTAL_RUNS
- Passed runs: REPLACE_PASSED_RUNS
- Overall pass rate: REPLACE_PASS_RATE
- Average latency: REPLACE_AVG_LATENCY

The evaluation records tool choices and latency for every run rather than judging the model from a single example.

---

## Why Multiple Runs Matter

LLM behavior is non-deterministic. A scenario that passes once may fail on another execution.

Running each scenario three times provides a more useful pass rate and exposes unstable tool-selection behavior.

For example, a scenario with 2 successful runs out of 3 has a 66.7% pass rate, which is more informative than reporting only one successful run.

---

## Trajectory Evaluation

The evaluation also checks which tool the model selected.

Examples of expected trajectories include:

- catalog request → `search_catalog`
- availability request → `check_book_availability`
- reservation request → `reserve_book`
- current-user reservation query → `get_my_reservations`
- general greeting → no tool

This provides more insight than checking only the final text response.

---

## Operational Metrics

The evaluation tracks:

- model-call count
- tool choice
- pass/fail result
- latency per run
- average latency

These metrics can later support:

- rate limiting
- caching
- model budgets
- timeout configuration
- performance monitoring

---

## LangSmith Tracing

LangSmith tracing was enabled using environment variables rather than hard-coding secrets.

The following were configured at runtime:

- `LANGSMITH_TRACING=true`
- `LANGSMITH_PROJECT=week7-agent-evaluation`
- `LANGSMITH_API_KEY` stored only as an environment variable

The API key was not committed to Git.

Tracing provides visibility into:

- model calls
- tool calls
- token usage
- latency
- execution trajectory

Only test data should be used in traces because traces can contain prompt and user information.

---

## Conclusion

Part G demonstrates that deterministic application logic should be verified with normal automated tests while LLM-driven decisions should be evaluated using repeated scenarios.

The combination of pytest, xUnit, repeated agent evaluations and tracing provides a more reliable way to understand system quality than manually testing a few prompts.