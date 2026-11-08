# Architecture Overview

## System Overview

The Hotel AI Assistant is a production-ready AI agent built with FastAPI that provides hotel guests with accurate, context-aware answers using Retrieval-Augmented Generation (RAG) and an LLM-powered agent with tool calling capabilities.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            HOTEL AI ASSISTANT                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │   Guest      │───▶│   FastAPI    │───▶│  ChatService │───▶│ AgentSvc │ │
│  │   (HTTP)     │    │   /chat      │    │  (orchestr)  │    │          │ │
│  └──────────────┘    └──────────────┘    └──────┬───────┘    └────┬─────┘ │
│                                                  │               │       │
│                    ┌─────────────────────────────┼───────────────┘       │
│                    ▼                             ▼                       │
│             ┌───────────────┐           ┌───────────────┐               │
│             │  RAG Service  │           │  Agent Tools  │               │
│             │  (ChromaDB)   │           │  (7 tools)    │               │
│             └───────┬───────┘           └───────┬───────┘               │
│                     │                           │                       │
│                     ▼                           ▼                       │
│             ┌───────────────┐           ┌───────────────┐               │
│             │  ChromaDB     │           │  LLM (Groq)   │               │
│             │  (Vector DB)  │           │  (Generation) │               │
│             └───────────────┘           └───────────────┘               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. FastAPI Application (`app/main.py`)
- **Entry point** with lifespan management
- **Middleware stack**: Correlation ID → Validation → Rate Limiting → CORS
- **Routes**: `/chat`, `/health`, `/metrics`, `/docs`
- **Dependency injection** via `AppContainer`

### 2. Chat Service (`app/services/chat_service.py`)
- **Orchestrator** between Agent and fallback RAG
- **Session management** via `session_id`
- **Fallback** to original RAG if agent fails

### 3. Agent Service (`app/agent/agent_service.py`)
- **IntentDetector**: LLM-based tool selection
- **ToolExecutor**: Executes tools, handles errors
- **AgentService**: Orchestrates detect → execute → respond loop

### 4. Tools (`app/agent/tools/`)
| Tool | Purpose |
|------|---------|
| `search_hotel_docs` | Semantic RAG search |
| `get_hotel_services` | Structured hotel info |
| `check_availability` | Mock room availability |
| `booking_management` | Create/view/cancel bookings |
| `special_requests` | Preferences, amenities, accessibility |
| `hotel_info` | Contact, location, directions |
| `escalate_to_human` | Forward to staff |

### 5. Memory System (`app/memory/`)
- **MemoryStore Interface** (InMemory + Redis implementations)
- **Conversation** model with TTL, max messages
- **Session isolation** via `session_id`

### 6. Services
| Service | Purpose |
|---------|---------|
| `LLMService` | Groq API with retries/timeouts |
| `EmbeddingService` | Google Gemini embeddings |
| `RAGService` | ChromaDB semantic search |
| `DocumentService` | Hotel document chunking |

### 7. Infrastructure
| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Vector DB | ChromaDB |
| LLM Provider | Groq (Groq Cloud) |
| Embeddings | Google Gemini |
| Cache/Session | Redis (prod) / In-Memory (dev) |
| Metrics | Prometheus |
| Logging | Structured JSON + Correlation IDs |
| Rate Limiting | slowapi (Redis/memory) |
| Validation | Custom middleware |
| Auth | API Key (X-API-Header) |

## Request Flow

```
1. Guest Request (HTTP POST /chat)
         │
         ▼
2. Correlation ID Middleware (generate/extract X-Correlation-ID)
         │
         ▼
         ▼
3. Validation Middleware (size, content-type, JSON)
         │
         ▼
4. Rate Limiting (slowapi: 100 req/min default)
         │
         ▼
5. API Key Auth (X-API-Key header)
         │
         ▼
6. FastAPI Route → ChatService.generate_response()
         │
         ├──▶ AgentService.process_message()
         │       │
         │       ├──▶ IntentDetector.detect_intent() → Tool selection
         │       │
         │       ├──▶ ToolExecutor.execute() → Tool result
         │       │
         │       └──▶ Response generation with context
         │
         └──▶ Fallback RAG (if agent fails)
                 │
                 ▼
7. Memory Store (save conversation)
         │
         ▼
8. Response (with session_id, message_count)
```

## Data Flow: RAG Pipeline

```
Hotel Document (data/hotel.txt)
         │
         ▼
DocumentService.split_into_chunks()
         │
         ▼
EmbeddingService.generate_embedding() → Vector (768 dim)
         │
         ▼
ChromaDB.add() → Vector + Document + ID
         │
         ▼
Query: "What time is check-in?"
         │
         ▼
EmbeddingService.generate_embedding() → Query Vector
         │
         ▼
ChromaDB.query(vector, n=3) → Top-K chunks
         │
         ▼
Distance threshold filter (≤ 0.9)
         │
         ▼
Relevant Context → LLM Prompt → Answer
```

## Configuration

### Environment-Based Settings (`app/settings/config.py`)
- **Pydantic Settings** with validation
- **Environment-specific** `.env.{environment}` files
- **Hotel customization** via env vars
- **Production-ready** defaults

### Key Settings Groups
| Category | Key Settings |
|----------|--------------|
| App | name, version, environment |
| Hotel | name, location, stars, contact |
| LLM | model, timeout, retries, API key |
| Embeddings | model, timeout, retries, API key |
| RAG | search limit, distance threshold |
| Memory | TTL, max messages |
| Rate Limit | requests, window |
| Redis | URL |
| Logging | level, format |

## Deployment Architecture

### Development
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   App       │     │  ChromaDB   │     │   In-Memory │
│  (uvicorn)  │────▶│  (local)    │     │   Memory    │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Production (Docker Compose)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   App       │────▶│   Redis     │     │  ChromaDB   │
│  (Docker)   │     │  (Sessions) │     │  (Docker)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Production Considerations
| Concern | Solution |
|---------|----------|
| Scalability | Stateless app, Redis for sessions |
| Reliability | Health checks, graceful shutdown |
| Observability | Prometheus metrics, structured logs |
| Security | API keys, rate limiting, validation |
| Scalability | Horizontal scaling via load balancer |
| Data persistence | Redis (sessions), ChromaDB (vectors) |

## Testing Strategy

| Level | Coverage |
|-------|----------|
| Unit | Services, tools, memory (mocked deps) |
| Integration | API endpoints, full flow |
| Memory | Session isolation, context carryover |
| Tools | All 7 tools with various inputs |

## Security

| Layer | Implementation |
|-------|----------------|
| Auth | API Key (X-API-Key header) |
| Rate Limiting | slowapi (100 req/min default) |
| Validation | Size limits (1MB), JSON validation |
| Headers | Correlation ID tracking |
| Secrets | Environment variables only |