# Hotel AI Assistant

An AI-powered assistant designed to help hotel guests get quick, useful answers to common questions using the hotel's own information.

Instead of searching through documents or contacting reception for every detail, guests can ask questions in natural language about check-in, hotel policies, services, and more. The goal is to make hotel information easier to access while keeping answers grounded in approved hotel content.

## The guest experience

A guest could ask:

> What time can I check in?

The assistant should retrieve the relevant hotel information and reply:

> Check-in starts at 15:00.

More sample conversations and use cases are available in the [Conversation Examples](docs/CONVERSATION_EXAMPLES.md) and the [User Guide](docs/USER_GUIDE.md).

## How it works

1. Hotel information is loaded from documents.
2. The text is split into smaller sections called *chunks*.
3. Embeddings represent the meaning of each section.
4. ChromaDB retrieves information relevant to a guest's question.
5. An LLM uses the retrieved context to formulate a natural-language answer.

This approach, known as **Retrieval-Augmented Generation (RAG)**, is intended to reduce unsupported answers by grounding responses in hotel-specific information.

## What's implemented

- **FastAPI** API foundation and a `/chat` endpoint.
- Loading hotel information from `data/hotel.txt`.
- Document chunking and embedding generation.
- ChromaDB storage and semantic retrieval.
- Initial retrieval checks, including a check-in question that retrieves the information stating 15:00.

The end-to-end path from API request through retrieval to a reliable final LLM answer still needs testing and improvement. See the [Features Roadmap](docs/FEATURES_ROADMAP.md) for the current scope and next milestones.

## Technology

Python · FastAPI · Retrieval-Augmented Generation (RAG) · Embeddings · ChromaDB · LLM

## Documentation

- [User Guide](docs/USER_GUIDE.md) — how guests could use the assistant.
- [Conversation Examples](docs/CONVERSATION_EXAMPLES.md) — sample guest messages and expected answers.
- [Features Roadmap](docs/FEATURES_ROADMAP.md) — implemented work, current priorities, and future features.
- [Architecture](docs/ARCHITECTURE.md) — the main components and how data flows through the system.

## Project status

**Early development.** Document processing and semantic retrieval have been implemented and initially tested. The main next step is to validate and stabilise the complete question-to-answer flow, then add automated tests, stronger error handling, and a simple guest-facing interface.

## Vision

The long-term goal is a practical assistant for the hospitality industry that can be configured with each hotel's information, answer routine questions at any time, and reduce repetitive enquiries to reception. Accuracy, clear limitations, and trustworthy answers are more important than simply producing a fluent response.
