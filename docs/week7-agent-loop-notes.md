# Week 7 Agent Loop Notes

## Challenge 1 — Step Limit

With `MAX_STEPS = 2`, the agent searched the catalog and found two science fiction books: Dune and Foundation. It then produced a partial response asking whether the user wanted the availability checked, but the graph immediately routed to the give-up node because the step limit had been reached. The user therefore saw both a useful partial answer and then the message: "I could not finish this within my step limit."

This is not an ideal user experience because the final failure message makes the interaction look broken even though useful progress was made. A better limit-hit experience should explain that the agent reached its safe execution limit, summarize what it completed, and clearly state what remains unfinished. It should avoid discarding useful results and should give the user a simple next action, such as asking whether they want to continue.

## Challenge 2 — Always-Failing Tool

### Prediction

If the agent calls a tool that always raises an exception, I expect the graph to fail unless the tool node handles the exception internally. If the exception is surfaced as a tool result instead of crashing, the agent may try the tool again or eventually stop at the step limit. I expect this challenge to show why tool failures should normally be returned as structured error data instead of raw exceptions.

### Actual Result

The prediction was correct. When `always_fail_tool` raised a `RuntimeError`, the LangGraph `ToolNode` propagated the exception and the whole graph stopped immediately. The agent did not retry the tool, did not reach the step limit, and did not produce a user-friendly apology. This shows that raw tool exceptions can crash the agent workflow and should normally be converted into structured error results that the graph can reason about.

### Conclusion

The default behavior was not acceptable for a user-facing agent because the user would receive a failed request instead of a useful explanation. A better design would catch tool failures and return structured error data such as `ERROR_RETRYABLE` or `ERROR_FINAL`, allowing the graph to decide whether to retry, re-plan, or stop safely.

## Challenge 3 — Hand-Drawn Graph vs Mermaid Graph

I first drew the graph manually as:

START → agent → tools → agent, with additional conditional paths from the agent to either `give_up` or `END`.

The state moving through the graph contains the message history and the current step count. When the agent calls a tool, the tool call is stored in an AI message, and after execution the tool result is appended as a ToolMessage before control returns to the agent.

The generated Mermaid diagram confirmed the same overall control flow. One thing my hand-drawn version initially missed was that all three possible routes from the agent node — `tools`, `give_up`, and `END` — are conditional edges from the same node rather than separate sequential stages.

The Mermaid graph also made the loop from `tools` back to `agent` more explicit, showing clearly how the think → act → observe cycle repeats until the agent finishes or reaches the step limit.