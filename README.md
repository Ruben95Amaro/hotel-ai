# Hotel AI Assistant

A production-ready AI agent for hotel guest assistance. Built with FastAPI, RAG, ChromaDB, and an LLM-powered agent with tool calling, conversation memory, and production-grade infrastructure.

## Features

- 🤖 **AI Agent** with 7 hotel-specific tools (search, booking, availability, special requests, etc.)
- 💬 **Conversation Memory** with session isolation and context carryover
- 🔐 **API Key Authentication** (dev mode bypass)
- 📊 **Prometheus Metrics** + Health Checks
- ⚡ **Rate Limiting** + Request Validation
- 📝 **Structured JSON Logging** with Correlation IDs
- 🐳 **Docker Support** for easy deployment
- 🧪 **Comprehensive Tests** (unit + integration)

## Quick Start

### Prerequisites
- Python 3.11+
- Groq API key (for LLM)
- Google Gemini API key (for embeddings)

### Installation

```bash
# Clone and navigate
cd hotel-ai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env.development
# Edit .env.development with your API keys:
# LLM_API_KEY=your_groq_key
# EMBEDDING_API_KEY=your_gemini_key

# Run the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker (recommended for production)

```bash
# Build and run
docker-compose up -d

# Or build manually
docker build -t hotel-ai .
docker run -p 8000:8000 --env-file .env.development hotel-ai
```

## API Usage

### Base URL
```
http://localhost:8000
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Main chat endpoint |
| `/health` | GET | Health check with dependencies |
| `/metrics` | GET | Prometheus metrics |
| `/docs` | GET | Swagger UI |

### Chat Endpoint

**Request:**
```json
POST /chat
Content-Type: application/json
X-API-Key: dev-key-12345

{
  "message": "What time is check-in?",
  "session_id": "optional-uuid-for-continuation"
}
```

**Response:**
```json
{
  "response": "Check-in starts at 15:00.",
  "session_id": "uuid-for-next-request",
  "message_count": 2
}
```

### Example Conversations

```bash
# First message (creates session)
curl -X POST http://localhost:8000/chat \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is check-in?"}'

# Follow-up (use returned session_id)
curl -X POST http://localhost:8000/chat \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"message": "What about check-out?", "session_id": "returned-uuid"}'

# New topic, same session
curl -X POST http://localhost:8000/chat \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"message": "What room types do you have?", "session_id": "same-uuid"}'

# New session (omit session_id)
curl -X POST http://localhost:8000/chat \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"message": "What facilities?"}'
```

## Configuration

### Environment Variables (`.env.development`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_API_KEY` | Yes | - | Groq API key |
| `EMBEDDING_API_KEY` | Yes | - | Google Gemini API key |
| `HOTEL_NAME` | No | Grand Ocean Hotel | Hotel name |
| `HOTEL_LOCATION` | No | Lisbon | Hotel location |
| `HOTEL_STARS` | No | 4 | Star rating |
| `HOTEL_PHONE` | No | +351 (XX) XXXX-XXXX | Contact phone |
| `HOTEL_EMAIL` | No | info@grandoceanhotel.com | Contact email |
| `API_KEYS` | No | ["dev-key-12345"] | Valid API keys (empty = no auth) |
| `RATE_LIMIT_REQUESTS` | No | 100 | Requests per window |
| `RATE_LIMIT_WINDOW` | No | minute | Time window |
| `CONVERSATION_TTL_SECONDS` | No | 86400 | Session TTL (24h) |
| `CONVERSATION_MAX_MESSAGES` | No | 50 | Max messages per session |
| `LOG_LEVEL` | No | INFO | Logging level |
| `LOG_FORMAT` | No | json | Log format (json/text) |
| `REDIS_URL` | No | redis://localhost:6379/0 | Redis for production memory |

### Hotel Customization

Update `.env.development` with your hotel details:
```env
HOTEL_NAME=Your Hotel Name
HOTEL_LOCATION=Your City
HOTEL_STARS=5
HOTEL_PHONE=+XX XXX XXXX
HOTEL_EMAIL=info@yourhotel.com
```

## Testing

```bash
# Run all tests
pytest test/ -v

# Run specific test files
pytest test/test_services.py -v      # Unit tests
pytest test/test_api.py -v           # Integration tests

# Run with coverage
pytest --cov=app test/
```

## Project Structure

```
hotel-ai/
├── app/
│   ├── api/              # FastAPI routes
│   ├── agent/            # AI Agent (tools, intent, executor)
│   ├── api/              # API routes
│   ├── di/               # Dependency injection container
│   ├── logging/          # Structured logging
│   ├── memory/           # Conversation memory (in-memory + Redis)
│   ├── middleware/       # Rate limiting, validation
│   ├── services/         # Core services (LLM, RAG, Embedding, etc.)
│   ├── settings/         # Configuration
│   └── main.py           # FastAPI app entry point
├── data/
│   └── hotel.txt         # Hotel knowledge base
├── test/
│   ├── test_services.py  # Unit tests
│   ├── test_api.py       # Integration tests
│   └── test_session_id.py # Session demo
├── docs/                 # Documentation
├── .env.example          # Env template
├── .env.development      # Local config (gitignored)
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container image
├── docker-compose.yml    # Multi-container setup
└── README.md             # This file
```

## Tools Available

| Tool | Description |
|------|-------------|
| `search_hotel_docs` | Semantic search in hotel docs |
| `get_hotel_services` | Structured hotel info (rooms, facilities, policies) |
| `check_availability` | Mock room availability with pricing |
| `booking_management` | Create/view/cancel/modify bookings |
| `special_requests` | Room prefs, amenities, accessibility |
| `hotel_info` | Contact, location, directions, attractions |
| `escalate_to_human` | Forward to hotel staff |

## Deployment

### Production Checklist
- [ ] Set `API_KEYS` with secure keys
- [ ] Configure `REDIS_URL` for session persistence
- [ ] Set `LOG_FORMAT=json` for log aggregation
- [ ] Configure reverse proxy (nginx/Traefik)
- [ ] Enable HTTPS
- [ ] Set up Prometheus + Grafana for metrics
- [ ] Configure log aggregation (ELK/Loki)

### Docker Compose (production)
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    build: .
    env_file: .env.production
    depends_on: [redis, chromadb]
  redis:
    image: redis:7-alpine
  chromadb:
    image: chromadb/chroma:latest
    volumes: [chroma_data:/data]
```

## License

MIT License — feel free to use and modify for your hotel.

---

**Built with** FastAPI, ChromaDB, Groq, Google Gemini, Prometheus, and ❤️ for hospitality.