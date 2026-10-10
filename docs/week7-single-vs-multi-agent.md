# Week 7 — Single-Agent vs Multi-Agent Recommendation

## Task Tested

The comparison used the same task:

> "Find me an available sci-fi book and reserve it."

The multi-agent system used a supervisor with two specialist workers:

- Catalog Agent — read-only catalog and availability work
- Circulation Agent — reservation/write work

## Multi-Agent Result

The supervisor selected the following sequence:

1. `catalog_agent`
2. `circulation_agent`
3. `FINISH`

The workflow successfully found an available science-fiction book and completed the reservation.

Measured result:

- Global supervisor steps: 3
- Model calls: 5
- Elapsed time: 88.96 seconds
- Reservation completed: Yes

The design also enforced least privilege because the Catalog Agent had no reservation capability and the Circulation Agent did not perform catalog discovery.

## Single-Agent Result

The same task was also tested using a single model workflow.

Measured result:

- Model calls: 1
- Elapsed time: 47.00 seconds

The single-agent approach required fewer model calls and less orchestration overhead.

## Comparison

The multi-agent architecture provides clearer separation of responsibilities and makes it easier to restrict tools by agent. Each specialist can also be tested independently, and least-privilege access becomes easier to enforce.

However, the multi-agent design required more model calls and significantly more execution time. In this test, the single-agent version used 1 model call and took 47.00 seconds, while the multi-agent version used 5 model calls and took 88.96 seconds.

The multi-agent system therefore introduced additional latency, routing logic, and more possible failure points.

## Recommendation

For the current library assistant, I would ship the single-agent design.

The current task is relatively small and can already be handled by one controlled agent using typed tools, approval controls, server-side authorization, idempotency, and retry logic. The measurements show that the multi-agent version adds substantial orchestration overhead without enough additional benefit for this scope.

The multi-agent architecture would become more useful if the system later grew to include many independent domains, much larger toolsets, or stronger permission boundaries between specialist agents.

The multi-agent prototype is still valuable because it demonstrates least-privilege agent design and clear separation between read-only catalog operations and write-capable circulation operations.

## Global Step Limit Test

A global step limit was added to prevent the supervisor from routing indefinitely between specialist agents.

The limit was tested by temporarily changing:

`MAX_GLOBAL_STEPS = 6`

to:

`MAX_GLOBAL_STEPS = 2`

The test result was:

- Global steps: 2
- Model calls: 3
- Reservation completed: False
- Elapsed time: 39.78 seconds

The workflow stopped before completing the reservation instead of continuing to loop between agents. This proves that the global step limit successfully provides a hard termination condition for the multi-agent system.