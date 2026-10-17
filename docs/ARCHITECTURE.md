# Architecture Overview

## Main components

### FastAPI

Exposes the HTTP API that receives a guest's question and returns the assistant's response. The current chat route is `/chat`.

### Document processing

Reads hotel content from `data/hotel.txt` and divides the text into smaller chunks. Smaller sections help retrieval focus on the part of the document most relevant to a question.

### Embeddings

Convert text into numerical vectors that represent semantic meaning. This allows the system to find relevant content even when the guest's wording differs from the wording in the source document.

### ChromaDB

Stores the vectors and associated text chunks and supports similarity search when a question arrives.

### LLM service

Uses the question and relevant retrieved hotel context to formulate a natural-language answer. The exact provider and model are configuration decisions and should not be assumed from this overview.

## Request flow

```text
Guest question
     |
     v
FastAPI /chat endpoint
     |
     v
RAG retrieval (embeddings + ChromaDB)
     |
     v
Relevant hotel context + guest question
     |
     v
LLM generates an answer
     |
     v
API response
```

The intended flow is shown above. The full end-to-end behaviour still needs validation, particularly that the retrieved context reaches the LLM and that the final response is grounded in that context.

## Why use RAG?

A general language model may not know a hotel's current policies and may produce plausible but incorrect details. RAG first searches the hotel's own information and supplies relevant passages to the model. This can improve relevance and traceability, but it does not guarantee correctness on its own. Retrieval quality, prompt design, fallback behaviour, and testing remain important.

## Current scope

The current foundation covers a single hotel information source and semantic retrieval. Multi-hotel isolation, production security, a guest-facing UI, monitoring, and integrations with reservation systems are future work rather than implemented capabilities.
