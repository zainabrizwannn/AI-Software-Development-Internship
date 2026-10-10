# Week 7 Tool Risk Table

| Tool | Read / Write | Needs Human Approval? | Idempotent? | Retryable? | Reason |
|---|---|---:|---:|---:|---|
| `search_catalog` | Read | No | Yes | Yes, for transient failures | It only retrieves catalog information and does not change stored data. |
| `check_book_availability` | Read | No | Yes | Yes, for transient failures | It only reads the current availability status of a book. |
| `reserve_book` | Write | Yes | Yes, using `Idempotency-Key` | Only for retryable/transient failures | It changes database state by creating a reservation, so the user must approve the exact book before execution. |

## Approval Justification

The read-only tools do not require human approval because they do not modify data, spend money, or perform irreversible actions. Requiring approval for every catalog lookup would add unnecessary friction without providing meaningful safety. The `reserve_book` tool requires approval because it changes persistent data and acts on behalf of the authenticated user. Retries of `reserve_book` are only safe when the same idempotency key is reused so that a repeated request cannot create duplicate reservations.