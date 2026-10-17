# Features Roadmap

This document separates confirmed project work from planned improvements. A feature should only be marked complete after it has been implemented and tested.

## Implemented foundations

- [x] FastAPI application foundation.
- [x] `/chat` API route defined for guest questions.
- [x] Read hotel information from `data/hotel.txt`.
- [x] Split document text into smaller chunks.
- [x] Generate embeddings for semantic retrieval.
- [x] Store and search chunks with ChromaDB.
- [x] Initial retrieval check for a question about check-in time.

## Current priority

- [ ] Validate the complete API flow: request → retrieval → LLM → response.
- [ ] Ensure the retrieved context is passed to the LLM correctly.
- [ ] Make the API request and response schemas consistent.
- [ ] Return a clear fallback when the retrieved context is insufficient.
- [ ] Add tests for known answers, unknown questions, malformed requests, and provider errors.
- [ ] Improve logging and error handling without exposing secrets or sensitive data.

## Next milestones

### Knowledge management

- [ ] Support multiple hotel documents and topics.
- [ ] Re-index documents when hotel information changes.
- [ ] Define a clear process for reviewing and approving hotel content.
- [ ] Add retrieval evaluation examples to detect regressions.

### Guest experience

- [ ] Build a simple chat interface for guests.
- [ ] Make fallback messages helpful and easy to understand.
- [ ] Consider multilingual questions and answers.
- [ ] Provide a clear route to hotel staff when the assistant cannot help.

### Production readiness

- [ ] Keep API keys and configuration in environment variables or a secrets manager.
- [ ] Add automated tests and a repeatable CI pipeline.
- [ ] Add authentication and rate limiting where appropriate.
- [ ] Monitor errors, latency, and answer quality while minimising personal data collection.
- [ ] Document deployment and operational procedures.

## Out of scope for the initial version

The initial version is an information assistant, not a booking engine. Changing reservations, processing payments, confirming live room availability, and accessing guest booking records would require integrations, access controls, and additional testing.
