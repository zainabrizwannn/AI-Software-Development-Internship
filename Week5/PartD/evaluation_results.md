# RAG Evaluation Results

This document records the evaluation of the manual RAG pipeline developed in Part D.

## Evaluation Table

| Question | Expected Answer | Retrieval Correct | Answer Correct |
|----------|-----------------|-------------------|----------------|
| What is Artificial Intelligence used for? | AI is used in healthcare, finance, education, and software development. | Yes | Yes |
| What does Python support? | Python is used for web development, data science, AI, and automation. | Yes | No |
| What do space missions use? | Space missions use satellites and telescopes. | Yes | Yes |
| When did the Industrial Revolution begin? | It began in the eighteenth century. | Yes | Yes |
| Who won the FIFA World Cup in 2022? | I don't have that information. | Yes | Yes |

---

## Failure Analysis

One failure was observed during testing.

**Question:**
What does Python support?

**Failure Type:**
Generation Failure

**Reason:**
The correct document (`python.txt`) was retrieved, but the model generated **"I don't have that information."** instead of answering from the retrieved context.

---

## Chunk Size Experiment

**Original Chunk Size:** 150

**New Chunk Size:** 75

### Observation

Reducing the chunk size improved retrieval focus while maintaining overall answer quality. Because the documents were relatively short, retrieval results remained mostly the same. Smaller chunks can improve retrieval precision for larger documents, although they may reduce surrounding context.

---

## Overall Conclusion

- The RAG pipeline successfully retrieved relevant document chunks for all test questions.
- Grounding the model with retrieved context helped reduce hallucinations.
- One generation failure was observed even though retrieval was correct, demonstrating the importance of evaluating retrieval and generation separately.
- Source attribution was successfully displayed for every retrieved answer.