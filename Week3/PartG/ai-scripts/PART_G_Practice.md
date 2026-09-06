## Practice 1 – Run the Script
### Prompt
Explain what a token is in one paragraph.

### Result
The script executed successfully and returned a paragraph explaining that a token is a unit of text processed by an AI model.

### Observation
This confirmed that:
- The Python virtual environment was working.
- The Gemini API key was configured correctly.
- The application successfully connected to the Gemini API.


## Practice 2 – Prompt Variations
### A. Plain Question
**Prompt**
What is a token in AI?

**Observation**
The AI answered the question in a simple explanatory style. It gave a general definition without following any special formatting or role.


### B. Direct Instruction
**Prompt**
Explain what a token is in exactly three sentences.

**Output Summary**
The AI explained that a token is a fundamental unit of text used by AI models and described how tokens help the model process language.

**Observation**
The AI followed the instruction and produced a concise response in the requested format.


### C. Role Based Prompt
**Prompt**
You are a strict librarian who only answers in one sentence. Explain what a token is.

**Output Summary**
"Lower your voice, because a token is simply a discrete, cataloged unit of text—such as a word, subword, or punctuation mark—that a computer system processes as a single piece of data."

**Observation**
The AI changed its tone and answered as a strict librarian in a single sentence, demonstrating that prompts can influence the style and behavior of the response.


## Practice 3 – Hallucination Test
**Prompt**
Who invented the XYZ-999 Quantum Library Language in 1852?

**Output Summary**
The AI stated that there is no record of an "XYZ-999 Quantum Library Language" and explained that the concept is fictional and historically inaccurate. It also provided historical context about quantum theory and Ada Lovelace.

**Observation**
Instead of inventing a fake inventor, the AI recognized that the concept does not exist and explained why. This shows that modern language models can avoid hallucinations by acknowledging when information is fictional or unsupported.
