# FailureAI — Software Failure Intelligence Platform

> Learn from software failures before they repeat.

[![CI](https://github.com/your-org/failure-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/failure-ai/actions/workflows/ci.yml)

---

## What is FailureAI?

FailureAI is an AI-powered platform for documenting, searching, and learning
from real-world software engineering failures. It combines:

- **Semantic search** — find related failures even with different wording
- **AI Assistant** — RAG-based chat grounded in the failure knowledge base
- **Risk Prediction** — input your tech stack, get failure risk scores
- **GitHub Integration** — import issues as structured failure reports

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Tailwind CSS, Vite |
| Backend | FastAPI (Python 3.11+), Pydantic v2 |
| Database | PostgreSQL 15 |
| Vector DB | ChromaDB |
| LLM | Gemini / OpenAI / Ollama (pluggable) |
| Auth | JWT (access + refresh tokens) |
| Deployment | Docker, Docker Compose |

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 4.x
- [Node.js](https://nodejs.org/) ≥ 20 (for local frontend dev)
- [Python](https://www.python.org/) ≥ 3.11 (for local backend dev)

### 1. Clone and configure

```bash
git clone https://github.com/your-org/failure-ai.git
cd failure-ai
cp .env.example .env
# Edit .env if needed (defaults work for local Docker dev)
```

### 2. Start the full stack

```bash
docker compose up --build
```

This starts:
| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/v1/health |
| PostgreSQL | localhost:5432 |
| ChromaDB | localhost:8001 |
| Redis | localhost:6379 |

### 3. Development mode (hot-reload)

```bash
# Backend + all services with hot-reload (uses docker-compose.override.yml automatically)
docker compose up

# Or run backend locally (faster iteration):
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# And frontend locally:
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
failure-ai/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py       # App entry point
│   │   ├── config.py     # Pydantic Settings
│   │   ├── database.py   # SQLAlchemy async engine
│   │   ├── models/       # ORM models (Week 2+)
│   │   ├── routers/      # API route handlers
│   │   └── core/         # Shared utilities
│   ├── alembic/          # Database migrations
│   ├── tests/            # pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React SPA
│   ├── src/
│   │   ├── App.tsx       # Router
│   │   ├── components/   # Shared components
│   │   ├── pages/        # Route pages
│   │   └── api/          # Axios API client
│   ├── Dockerfile
│   └── package.json
├── .github/workflows/    # GitHub Actions CI
├── docker-compose.yml    # Production-like stack
├── docker-compose.override.yml  # Dev hot-reload overrides
└── .env.example          # Environment variable template
```

---

## Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend linting
cd frontend
npm run lint
npm run build
```

---

## Roadmap

| Week | Phase |
|---|---|
| ✅ Week 1 | Project Setup & Infrastructure |
| Week 2 | Core CRUD (Auth, Projects, Failures) |
| Week 3 | Semantic Search |
| Week 4 | AI Assistant |
| Week 5 | Dashboard & Analytics |
| Week 6 | GitHub Integration |
| Week 7 | Risk Prediction |
| Week 8 | Hardening & Production Launch |

---

## Contributing

1. Create a branch from `main`
2. Make your changes
3. Ensure CI passes: `pytest` + `npm run lint` + `npm run build`
4. Open a pull request

## License

MIT
