## Challenge 2 - Why Immediate Retries Without Backoff Are Harmful

If the AI service is already slow, overloaded, or temporarily unavailable, retrying immediately can make the problem worse.

Without backoff, many requests may retry again at almost the same time.

This can create additional load on a service that is already struggling.

For example:

- the first request fails
- the client retries immediately
- many other clients may also retry immediately
- the AI service receives even more traffic
- recovery becomes slower

Using exponential backoff reduces this pressure.

In this implementation, retries wait progressively longer:

- first retry: 2 seconds
- second retry: 4 seconds
- third retry: 8 seconds

This gives the downstream AI service time to recover and reduces the chance of creating a retry storm.

## Challenge 3 - Why Retrying a Partially Successful Request Can Be Dangerous

Not every failed request is safe to retry.

A request may fail from the caller's point of view even though the AI service already started processing it.

For example, the AI service may already have:

- sent a request to a paid AI provider
- started generating a response
- consumed tokens
- recorded data
- performed another side effect

If the .NET API automatically retries the same request, the AI service may repeat that work.

This could cause:

- duplicate paid API calls
- extra token usage
- duplicate database changes
- repeated side effects
- increased cost

Because of this, retry policies should only retry failures that are likely to be transient and safe to repeat.

Examples of transient failures include:

- temporary network failures
- connection errors
- HTTP 5xx responses
- short-lived service unavailability

Requests with important side effects should be designed carefully before enabling automatic retries.