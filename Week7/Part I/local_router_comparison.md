# Optional Local Model Router Comparison

The router was tested using the local Ollama model:

`llama3.2:3b`

The routing evaluation used the same 15 messages from Part C.

Results from the previous router evaluation:

- Total test messages: 15
- Correct classifications: 15
- Routing accuracy: 100%

The local model was slower than a lightweight hosted classification model would normally be, but it had two major advantages:

- no external model API cost
- prompts and routing data remained on the local machine

For a small classification task such as routing between `catalog`, `action`, and `chitchat`, the local model was good enough in this test.

For more complex reasoning tasks, a larger or hosted model may still provide better quality and lower latency depending on the available hardware.

## Conclusion

For the router node, the local Ollama model was acceptable because classification required a small output space and achieved 15/15 correct classifications.

I would consider using a local model for simple routing while reserving a stronger model for more difficult reasoning tasks.