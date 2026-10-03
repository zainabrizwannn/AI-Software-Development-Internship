## Challenge 1 - Visible Streaming

The Angular chat interface successfully displays the AI response while it is being streamed through the .NET proxy.

The response is received as SSE chunks and appended to the UI as each chunk arrives, instead of waiting for the complete response.

Flow:

Angular -> .NET API -> FastAPI -> Gemini
Gemini -> FastAPI SSE -> .NET proxy -> Angular

The interface displays "Streaming..." while the response is still being received.
## Challenge 2 - Deliberately Slow the Stream

To verify that the response was genuinely streamed rather than returned as one complete response, a deliberate delay was added between FastAPI chunks.

```python
time.sleep(0.3)

## Challenge 3 - FlushAsync

The explicit `FlushAsync()` call was temporarily removed from the .NET streaming proxy.

Without explicitly flushing each SSE chunk, the streaming behavior no longer worked reliably in the Angular client. In this test, Angular displayed "Unable to stream the AI response."

`FlushAsync()` was restored after the experiment.

The flush is important because it forces data written to the response body to be sent toward the client immediately rather than remaining buffered.

## Challenge 4 - Cancel Streaming on Navigation

The Angular chat component uses an AbortController for the streaming fetch request.

When the component is destroyed, `ngOnDestroy()` calls the stop method, which aborts the active request.

The .NET streaming endpoint also receives a CancellationToken and passes it to the upstream HTTP request and stream-reading operations.

Therefore, when the user navigates away from the chat page during an active stream, the browser request is cancelled and the cancellation propagates through the .NET proxy instead of leaving the upstream request running unnecessarily.

