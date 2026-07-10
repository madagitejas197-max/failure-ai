# Technical Requirements Document (TRD)
## FailureAI — Software Failure Intelligence Platform

| | |
|---|---|
| **Document owner** | Engineering |
| **Status** | Draft v1.0 |
| **Last updated** | 2026-07-10 |
| **Related docs** | prd.md, implementation-plan.md |

---

## 1. Purpose

This document translates the PRD into a concrete technical design:
architecture, data model, API contracts, AI/ML pipeline, security, and
operational requirements needed to build FailureAI.

## 2. System Architecture

### 2.1 High-level architecture

```
┌─────────────────┐        ┌──────────────────────┐        ┌────────────────┐
│  React + Tailwind│  HTTPS │      FastAPI          │        │   PostgreSQL   │
│  Frontend (SPA)   ├───────►│  (REST API, JWT auth) ├───────►│  (relational)  │
└─────────────────┘        │                        │        └────────────────┘
                            │  ┌──────────────────┐  │
                            │  │ Embedding Service │──┼──────► ┌────────────────┐
                            │  └──────────────────┘  │        │   ChromaDB      │
                            │  ┌──────────────────┐  │        │  (vector store) │
                            │  │  LLM Gateway      │  │        └────────────────┘
                            │  │ (Gemini/OpenAI/   │  │
                            │  │  Ollama adapter)  │  │
                            │  └──────────────────┘  │
                            │  ┌──────────────────┐  │
                            │  │ GitHub Import Job │──┼──────► GitHub REST/GraphQL API
                            │  └──────────────────┘  │
                            └──────────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Object Storage    │  (logs, screenshots)
                            │  (S3-compatible)   │
                            └──────────────────┘
```

All backend services are containerized and deployed via Docker
(Docker Compose for dev, orchestrated deployment for prod — see §9).

### 2.2 Component responsibilities

| Component | Responsibility |
|---|---|
| Frontend (React + Tailwind) | SPA UI, client-side routing, auth token storage, calls REST API |
| Backend API (FastAPI) | Business logic, auth, validation, orchestration of AI calls |
| PostgreSQL | System of record for structured data (users, projects, failures, comments, tags) |
| ChromaDB | Vector store for failure embeddings, powers semantic search |
| LLM Gateway | Abstraction layer over Gemini / OpenAI / Ollama for chat + extraction tasks |
| Embedding Service | Generates embeddings for failure text on create/update |
| GitHub Import Job | Async worker that pulls issues and drafts structured failures |
| Object Storage | Stores uploaded screenshots and large log files |
| Background worker/queue | Handles embedding generation, GitHub sync, notification, moderation scans |

### 2.3 Tech stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React 18+, Tailwind CSS, Recharts | SPA; component library TBD (e.g. shadcn/ui) |
| Backend | FastAPI (Python 3.11+) | Async, Pydantic v2 for schemas |
| Database | PostgreSQL 15+ | Primary data store |
| Vector DB | ChromaDB | Embedding storage + similarity search |
| LLM Providers | Gemini, OpenAI, Ollama (self-hosted fallback) | Pluggable via LLM Gateway interface |
| Auth | JWT (access + refresh tokens) | `python-jose` or equivalent |
| Task queue | Celery or FastAPI BackgroundTasks + Redis | For async embedding/import jobs |
| Object storage | S3-compatible (AWS S3 / MinIO for self-host) | Logs, screenshots |
| Deployment | Docker, Docker Compose (dev), Kubernetes or managed container service (prod) | See §9 |
| CI/CD | GitHub Actions | Lint, test, build, deploy pipelines |

## 3. Data Model

### 3.1 Entity-relationship summary

```
Users ──< Projects ──< Failures ──< Comments
                          │  │
                          │  └──< Embeddings (1:1 per failure, stored in ChromaDB, referenced by id)
                          │
Tags ──────────────────────< FailureTags (M:N)
                          │
ImportedIssues ───────────┘ (source of Failures created via GitHub import)
```

### 3.2 Table definitions

**users**
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| email | varchar, unique | |
| password_hash | varchar | nullable if OAuth-only |
| display_name | varchar | |
| avatar_url | varchar | |
| bio | text | |
| role | enum(user, moderator, admin) | default `user` |
| github_id | varchar, nullable | for OAuth linkage |
| created_at / updated_at | timestamptz | |

**projects**
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| owner_id | UUID FK → users.id | |
| name | varchar | |
| description | text | |
| tech_stack | text[] / jsonb | denormalized list for quick filtering |
| visibility | enum(public, org, private) | |
| created_at / updated_at | timestamptz | |

**failures**
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| project_id | UUID FK → projects.id, nullable | nullable if standalone submission |
| author_id | UUID FK → users.id | |
| category | enum(architecture, security, performance, deployment, scaling, data, other) | |
| tech_stack | text[] / jsonb | |
| title | varchar | |
| problem | text | |
| root_cause | text | |
| solution | text | |
| lesson_learned | text | |
| severity | enum(low, medium, high, critical) | |
| logs_redacted | text, nullable | post secret-scan |
| github_url | varchar, nullable | |
| time_to_detect_seconds | integer, nullable | |
| time_to_resolve_seconds | integer, nullable | |
| visibility | enum(public, org, private) | |
| status | enum(draft, published, flagged, archived) | |
| embedding_id | varchar, nullable | reference into ChromaDB collection |
| upvote_count | integer | default 0 |
| created_at / updated_at | timestamptz | |

**comments**
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| failure_id | UUID FK → failures.id | |
| author_id | UUID FK → users.id | |
| body | text | |
| created_at / updated_at | timestamptz | |

**tags**
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| name | varchar, unique | |
| category | varchar, nullable | e.g. "language", "database", "cloud" |

**failure_tags** (join table)
| Column | Type |
|---|---|
| failure_id | UUID FK |
| tag_id | UUID FK |

**embeddings** (metadata table; vectors live in ChromaDB)
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | matches ChromaDB document id |
| failure_id | UUID FK → failures.id | |
| model_name | varchar | embedding model used |
| model_version | varchar | |
| created_at | timestamptz | |

**imported_issues**
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| repo_full_name | varchar | e.g. `org/repo` |
| github_issue_id | bigint | |
| github_issue_url | varchar | |
| imported_by | UUID FK → users.id | |
| draft_failure_id | UUID FK → failures.id, nullable | set once converted |
| raw_payload | jsonb | original issue payload |
| status | enum(pending, drafted, published, rejected) | |
| created_at / updated_at | timestamptz | |

**risk_predictions** (supports Risk Prediction feature + explainability)
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| requested_by | UUID FK → users.id | |
| project_type | varchar | |
| tech_stack | text[] | |
| risk_score | numeric | 0–100 |
| predicted_categories | jsonb | ranked list with confidence |
| evidence_failure_ids | UUID[] | failures used as evidence |
| model_version | varchar | |
| created_at | timestamptz | |

**audit_logs**
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| actor_id | UUID FK → users.id, nullable | nullable for system actions |
| action | varchar | e.g. `failure.delete` |
| resource_type / resource_id | varchar / UUID | |
| metadata | jsonb | |
| created_at | timestamptz | |

## 4. API Design

Base path: `/api/v1`. All endpoints return JSON; errors follow a consistent
envelope: `{ "error": { "code": str, "message": str, "details": obj|null } }`.

### 4.1 Auth
| Method | Path | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Create account | Public |
| POST | `/auth/login` | Email/password login, returns access+refresh JWT | Public |
| POST | `/auth/refresh` | Exchange refresh token for new access token | Refresh token |
| POST | `/auth/logout` | Invalidate refresh token | Access token |
| GET | `/auth/github/callback` | OAuth callback | Public |
| GET | `/users/me` | Current user profile | Access token |
| PUT | `/users/me` | Update profile | Access token |

### 4.2 Projects
| Method | Path | Description |
|---|---|---|
| GET | `/projects` | List projects (filterable) |
| POST | `/projects` | Create project |
| GET | `/projects/{id}` | Get project |
| PUT | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project (owner/admin only) |

### 4.3 Failures
| Method | Path | Description |
|---|---|---|
| GET | `/failures` | List/filter failures (category, severity, tech_stack, date range, project) |
| POST | `/failures` | Create failure (triggers async embedding job) |
| GET | `/failures/{id}` | Get failure detail |
| PUT | `/failures/{id}` | Update failure (re-triggers embedding on content change) |
| DELETE | `/failures/{id}` | Soft-delete/archive failure |
| POST | `/failures/{id}/upvote` | Upvote a failure |
| GET | `/failures/{id}/comments` | List comments |
| POST | `/failures/{id}/comments` | Add comment |

### 4.4 Search
| Method | Path | Description |
|---|---|---|
| POST | `/search` | Hybrid semantic + keyword search. Body: `{ query, filters, limit, offset }` |

### 4.5 AI Assistant
| Method | Path | Description |
|---|---|---|
| POST | `/assistant/chat` | Send message, returns grounded response with `sources: [failure_id]` |
| GET | `/assistant/checklist` | Generate prevention checklist for `{category, tech_stack}` |

### 4.6 Dashboard
| Method | Path | Description |
|---|---|---|
| GET | `/dashboard/trends` | Failure trend time series |
| GET | `/dashboard/tech-comparison` | Comparison metrics across tech stacks |
| GET | `/dashboard/severity-distribution` | Severity breakdown |
| GET | `/dashboard/avg-fix-time` | Avg time-to-resolve by category/stack |

### 4.7 GitHub Integration
| Method | Path | Description |
|---|---|---|
| POST | `/github/connect` | Store OAuth token for repo access |
| GET | `/github/repos` | List accessible repos |
| POST | `/github/import` | Trigger import job for selected issues (async) |
| GET | `/github/import/{job_id}` | Poll import job status |
| GET | `/imported-issues` | List imported issue drafts |

### 4.8 Risk Prediction
| Method | Path | Description |
|---|---|---|
| POST | `/predict` | Body: `{ project_type, tech_stack, scale? }` → risk score + evidence |
| GET | `/predict/{id}` | Retrieve a past prediction |

### 4.9 Admin/Moderation
| Method | Path | Description |
|---|---|---|
| GET | `/admin/flagged` | List flagged content |
| POST | `/admin/failures/{id}/moderate` | Approve/reject/redact |
| GET | `/admin/audit-logs` | Query audit logs |

## 5. AI / ML Pipeline

### 5.1 Embedding pipeline
1. On failure create/update (status transitions to `published`), enqueue an
   embedding job.
2. Worker concatenates `title + problem + root_cause + solution +
   lesson_learned` into a normalized document.
3. Generate embedding via configured provider (default: a sentence-embedding
   model; provider abstracted behind the same LLM Gateway interface).
4. Upsert vector into ChromaDB collection `failures`, with metadata
   (`failure_id`, `category`, `severity`, `tech_stack`, `visibility`) for
   filtered similarity search.
5. Record embedding metadata row in Postgres `embeddings` table.

### 5.2 Semantic search flow
1. Embed the incoming query using the same model as indexing.
2. Query ChromaDB for top-K nearest neighbors, applying metadata filters
   (category/severity/tech_stack/visibility) at query time.
3. Optionally re-rank top-K using a lightweight cross-encoder or LLM-based
   rerank for higher precision.
4. Merge with keyword search results (Postgres full-text search) using a
   weighted hybrid score; return combined, deduplicated results.

### 5.3 AI Assistant grounding
- Assistant uses retrieval-augmented generation (RAG): user query →
  semantic search over failures → top-N results injected into LLM context
  → LLM instructed to answer only using provided context and cite
  `failure_id`s.
- System prompt enforces: "If the answer is not supported by the provided
  failure reports, say so explicitly rather than fabricating."
- Every response returns a `sources` array mapped to UI citation chips.

### 5.4 GitHub import extraction
- Fetch issue title/body/comments via GitHub API.
- LLM extraction prompt maps issue content to the Failure Submission schema
  (category, tech stack, problem, root cause, solution, lesson learned)
  with a structured JSON output contract.
- Output validated against a strict JSON schema before being stored as an
  `imported_issues` draft; malformed extractions are retried once, then
  flagged for manual entry.

### 5.5 Risk Prediction model
- v1 approach: retrieval-based scoring — given `project_type` +
  `tech_stack`, query the failure corpus for historically similar
  combinations, aggregate severity/frequency into a weighted risk score,
  and rank failure categories by observed frequency in the matched set.
- LLM used to generate human-readable recommendations from the aggregated
  evidence (not to invent the score itself) — keeps the score deterministic
  and explainable.
- Designed to be swappable for a trained ML model (e.g. gradient-boosted
  classifier) once sufficient labeled outcome data exists (Future scope).

### 5.6 LLM Gateway abstraction
A single internal interface (`LLMProvider`) with implementations for
Gemini, OpenAI, and Ollama, selected via configuration/env var, so:
- Providers can be swapped without touching business logic.
- Self-hosted Ollama can be used as a cost-free/offline fallback.
- Prompts and output schemas are provider-agnostic.

## 6. Security

- **Authentication**: JWT access tokens (short-lived, e.g. 15 min) +
  refresh tokens (longer-lived, rotated on use, stored hashed).
- **Authorization**: Role-based (`user`/`moderator`/`admin`) plus
  resource-level ownership checks (author or org-member can edit/delete;
  admins/moderators can moderate).
- **Secret scanning**: All submitted logs and free-text fields scanned for
  credential patterns (API keys, tokens, connection strings) before
  storage; matches auto-redacted, submission flagged for review.
- **Input validation**: Pydantic schemas on all endpoints; strict length
  and content-type limits on uploads.
- **Rate limiting**: Per-user and per-IP rate limits on submission, search,
  and AI Assistant endpoints to control abuse and LLM cost.
- **Transport security**: HTTPS enforced everywhere; secure, HttpOnly,
  SameSite cookies if cookie-based storage is used for refresh tokens.
- **Audit logging**: All mutating actions logged with actor, action,
  resource, and timestamp (see `audit_logs` table).
- **Data privacy**: Users can request export/deletion of their data;
  private/org-visibility failures excluded from public search and from
  cross-tenant LLM context.

## 7. Non-Functional Requirements (technical detail)

| Requirement | Target |
|---|---|
| CRUD endpoint latency | < 2s p95 |
| Search endpoint latency | < 3s p95 (embedding + vector query + rerank) |
| AI Assistant response (first token) | < 3s p95 (streaming) |
| Availability | 99.5% monthly uptime |
| Embedding job processing lag | < 30s from publish to searchable, p95 |
| Horizontal scalability | Stateless API layer; scale API and worker pods independently |
| Data durability | Postgres daily automated backups; object storage versioning enabled |

## 8. Observability

- Structured JSON logging across API and workers.
- Metrics: request latency/error rate per endpoint, embedding job queue
  depth, LLM call latency/cost per provider, search relevance click-through
  rate.
- Tracing across API → embedding worker → vector DB → LLM Gateway for
  debugging slow requests.
- Alerting on error rate spikes, queue backlog, and LLM provider failures
  (with automatic fallback to secondary provider where configured).

## 9. Deployment Architecture

- **Dev**: Docker Compose bringing up API, worker, Postgres, ChromaDB,
  Redis, and frontend dev server together.
- **Staging/Prod**: Containers built via CI, deployed to a container
  orchestration platform (Kubernetes or equivalent managed service);
  Postgres and object storage as managed services where possible.
- **CI/CD**: GitHub Actions pipeline — lint → unit tests → build images →
  integration tests → deploy to staging → manual promote to prod.
- **Environments**: `dev`, `staging`, `prod`, each with isolated config
  (LLM API keys, DB credentials) via secrets manager.
- **Migrations**: Alembic (or equivalent) for Postgres schema migrations,
  run as a pre-deploy step.

## 10. Testing Strategy

| Layer | Approach |
|---|---|
| Unit tests | Backend business logic, schema validation, LLM Gateway adapters (mocked) |
| Integration tests | API endpoints against a test Postgres + Chroma instance |
| Search relevance eval | Curated query/expected-result set to catch embedding/ranking regressions |
| E2E tests | Critical user flows (register → submit failure → search → find it) via Playwright/Cypress |
| Load testing | Search and CRUD endpoints against NFR latency targets |
| Security testing | Dependency scanning, basic OWASP checks, secret-scan false-negative testing |

## 11. Open Technical Decisions

- Task queue choice: Celery+Redis vs. lightweight FastAPI BackgroundTasks
  for v1 (recommend Celery+Redis once GitHub import + embedding volume
  justify it).
- Default LLM provider for cost-sensitive endpoints (Assistant vs.
  extraction) — likely different providers/models per use case.
- Whether ChromaDB runs embedded/local vs. as a standalone service in prod
  (recommend standalone service for durability and scaling).
