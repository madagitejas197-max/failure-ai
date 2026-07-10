# Implementation Plan
## FailureAI — Software Failure Intelligence Platform

| | |
|---|---|
| **Document owner** | Engineering |
| **Status** | Draft v1.0 |
| **Last updated** | 2026-07-10 |
| **Related docs** | prd.md, trd.md |
| **Timeline** | 8 weeks to v1 launch |

---

## 1. Assumptions

- Team: 1 backend engineer, 1 frontend engineer, 1 full-stack/ML-leaning
  engineer, part-time design/product support. Adjust parallelism if team
  size differs.
- Single environment progression: local → staging → prod.
- LLM provider access (Gemini/OpenAI API keys, or local Ollama) available
  from Week 1.
- Docker/Docker Compose used from day one to avoid environment drift.

## 2. Phase Breakdown

### Phase 1 — Week 1: Project Setup & Infrastructure

**Goal**: A running skeleton (empty frontend + backend + DB) deployed to
staging, with CI green.

Tasks:
- [ ] Initialize monorepo (or separate `frontend/` and `backend/` repos)
- [ ] Scaffold FastAPI project: app structure, config management, env
      handling, health-check endpoint
- [ ] Scaffold React + Tailwind project: routing, base layout, API client
      wrapper
- [ ] Provision PostgreSQL (dev via Docker, staging via managed service)
- [ ] Provision ChromaDB instance (dev container, staging service)
- [ ] Set up Alembic migrations, initial empty migration
- [ ] Docker Compose for local dev (API + worker + Postgres + ChromaDB +
      Redis + frontend)
- [ ] GitHub Actions CI: lint (ruff/eslint), unit test runner, build
      pipeline
- [ ] Deploy skeleton to staging; confirm health-check reachable
- [ ] Secrets management setup (LLM API keys, DB creds) for staging

**Deliverables**: Running skeleton app in staging, CI pipeline green,
migration tooling in place.

**Exit criteria**: `docker compose up` brings up full stack locally;
staging health endpoint returns 200.

---

### Phase 2 — Week 2: Core CRUD (Auth, Users, Projects, Failures)

**Goal**: Users can register, log in, and perform full CRUD on Projects
and Failures (without search/AI yet).

Backend tasks:
- [ ] `users`, `projects`, `failures`, `tags`, `failure_tags`,
      `comments`, `audit_logs` tables + migrations
- [ ] Auth endpoints: register, login, refresh, logout; JWT issuance and
      validation middleware
- [ ] GitHub OAuth login flow
- [ ] Role-based authorization middleware (`user`/`moderator`/`admin`)
- [ ] Projects CRUD endpoints
- [ ] Failures CRUD endpoints (draft/publish status, ownership checks)
- [ ] Comments + upvote endpoints
- [ ] Secret-scanning utility for logs field on submission
- [ ] Audit logging middleware/decorator applied to mutating endpoints
- [ ] Unit + integration tests for all above

Frontend tasks:
- [ ] Register / Login / GitHub OAuth UI
- [ ] Auth state management (token storage, refresh handling, protected
      routes)
- [ ] Profile page (view/edit)
- [ ] Failure submission form (all fields from PRD §6.2), draft/publish
      flow
- [ ] Failure list + detail view
- [ ] Project list + detail view
- [ ] Comment thread UI + upvote button

**Deliverables**: End-to-end flow — register → create project → submit
failure → view it — works in staging.

**Exit criteria**: Core CRUD API test suite passing; manual QA of primary
flows complete.

---

### Phase 3 — Week 3: Semantic Search

**Goal**: Failures are embedded on publish and searchable semantically.

Tasks:
- [ ] Implement LLM Gateway abstraction with embedding method (provider
      configurable: Gemini/OpenAI/Ollama)
- [ ] Background worker: embedding job triggered on failure
      create/update/publish
- [ ] ChromaDB collection setup with metadata schema (category, severity,
      tech_stack, visibility)
- [ ] `POST /search` endpoint: query embedding → vector similarity search
      → metadata filtering → optional keyword hybrid merge
- [ ] Postgres full-text search index as keyword fallback/hybrid signal
- [ ] Build curated relevance eval set (10–20 query/expected-result pairs)
      for regression testing
- [ ] Frontend: search bar, filters (category/severity/tech
      stack/date), results list with relevance/citation info
- [ ] Backfill: script to embed any pre-seeded/imported content

**Deliverables**: Working semantic search in staging with filters.

**Exit criteria**: Relevance eval set passes threshold (e.g. top-3
precision ≥ target agreed with product); search latency within NFR.

---

### Phase 4 — Week 4: AI Assistant

**Goal**: Conversational assistant grounded in the failure knowledge base.

Tasks:
- [ ] Design RAG prompt templates (chat, checklist generation)
- [ ] `POST /assistant/chat` endpoint: retrieve top-N relevant failures →
      inject as context → call LLM → return response with `sources`
- [ ] `GET /assistant/checklist` endpoint for prevention checklists by
      category/tech stack
- [ ] Streaming response support (SSE or chunked) for chat UI
      responsiveness
- [ ] Guardrails: refuse/qualify answers when no supporting evidence found
- [ ] Frontend: chat UI with citation chips linking back to failure
      reports; checklist view
- [ ] Rate limiting on assistant endpoints (cost control)
- [ ] Manual eval pass: spot-check assistant answers for hallucination/
      unsupported claims

**Deliverables**: AI Assistant available in staging, answers cite sources.

**Exit criteria**: No unsourced claims in eval spot-check; latency within
NFR (first token < 3s p95).

---

### Phase 5 — Week 5: Dashboard & Analytics

**Goal**: Trend and comparison visualizations powered by real submission
data.

Tasks:
- [ ] Aggregation queries: trends over time, severity distribution,
      tech-stack comparison, avg time-to-resolve
- [ ] `GET /dashboard/*` endpoints with caching (materialized view or
      periodic aggregation job for expensive queries)
- [ ] Frontend dashboard using Recharts: trend line/area charts, severity
      pie/bar chart, tech comparison table/chart, avg fix-time chart
- [ ] Personal vs. org-level dashboard scoping
- [ ] Performance test dashboard endpoints under representative data
      volume

**Deliverables**: Dashboard live in staging with real data from Phases
1–4 submissions/seed data.

**Exit criteria**: Dashboard endpoints meet CRUD latency NFR; charts
render correctly across data volume test.

---

### Phase 6 — Week 6: GitHub Integration

**Goal**: Users can import GitHub issues as structured draft failure
reports.

Tasks:
- [ ] GitHub App/OAuth scope for repo read access (`/github/connect`)
- [ ] `GET /github/repos` — list accessible repos
- [ ] Async import job: fetch issues (filter by label), LLM extraction
      into structured schema, validate against JSON schema, store as
      `imported_issues` + draft `failures`
- [ ] `POST /github/import`, `GET /github/import/{job_id}` polling
      endpoints
- [ ] Frontend: repo connect flow, issue selection UI, import job status,
      draft review/edit screen before publish
- [ ] Retry/error handling for malformed LLM extraction output
- [ ] Tests: mocked GitHub API responses, extraction schema validation

**Deliverables**: End-to-end GitHub import flow working in staging with a
real test repository.

**Exit criteria**: Imported drafts never auto-publish; review UI
functional; error/retry path verified.

---

### Phase 7 — Week 7: Risk Prediction

**Goal**: Users can input a project type + tech stack and receive an
explainable risk score.

Tasks:
- [ ] Retrieval-based scoring implementation: query corpus for similar
      project_type/tech_stack combinations, aggregate severity/frequency
- [ ] `POST /predict` endpoint: returns risk score, ranked predicted
      categories, evidence failure IDs, LLM-generated recommendations
- [ ] `risk_predictions` table + `GET /predict/{id}` retrieval endpoint
- [ ] Frontend: prediction input form, results view with score breakdown
      and linked evidence failures
- [ ] Versioning: store `model_version` on each prediction for future
      comparison
- [ ] Validate explainability: every score traceable to underlying
      evidence in UI

**Deliverables**: Risk Prediction feature live in staging.

**Exit criteria**: Predictions are explainable (evidence shown), latency
within NFR, spot-checked for reasonableness against seed data.

---

### Phase 8 — Week 8: Hardening & Deployment

**Goal**: Production-ready, secure, observable v1 launch.

Tasks:
- [ ] Full security pass: rate limiting on all public endpoints, secret
      scanning coverage review, dependency vulnerability scan
- [ ] Load testing against NFR targets (CRUD, search, assistant,
      dashboard)
- [ ] Observability: structured logging, metrics dashboards (latency,
      error rate, queue depth, LLM cost/latency), alerting rules
- [ ] Backup/restore drill for Postgres; object storage versioning
      confirmed
- [ ] Production infrastructure provisioning (Kubernetes/managed
      container service, managed Postgres, object storage, secrets
      manager)
- [ ] Final CI/CD promotion pipeline: staging → prod with manual approval
      gate
- [ ] Content seeding: curated public postmortems imported/published pre-
      launch to avoid empty-state problem
- [ ] Moderation tooling smoke test (`/admin/flagged`, moderate actions)
- [ ] Documentation: README, API docs (OpenAPI via FastAPI), runbook for
      on-call
- [ ] Go/no-go review against exit criteria of all prior phases
- [ ] Production launch

**Deliverables**: v1 live in production.

**Exit criteria**: All NFRs met in prod-like load test; security checklist
signed off; rollback plan documented and tested.

## 3. Cross-Cutting Workstreams (run throughout all phases)

| Workstream | Notes |
|---|---|
| Design/UX | Component library and design system established by end of Week 2; used consistently thereafter |
| QA | Manual test pass at the end of every phase against that phase's exit criteria |
| Documentation | API docs auto-generated (OpenAPI) kept current each phase; user-facing docs drafted in Week 7–8 |
| Cost monitoring | Track LLM API spend weekly starting Phase 3; adjust provider/caching strategy if trending over budget |

## 4. Dependencies & Sequencing Notes

- Phase 3 (Search) depends on Phase 2's Failure schema being stable —
  avoid major schema changes to `failures` after Week 2 without a
  migration + re-embedding plan.
- Phase 4 (Assistant) depends on Phase 3 (Search) for retrieval —
  cannot start meaningfully early.
- Phase 6 (GitHub Import) can be developed in parallel with Phase 5
  (Dashboard) if team capacity allows, since they don't share critical
  path dependencies beyond core CRUD.
- Phase 7 (Risk Prediction) depends on a reasonable volume of embedded
  failure data (Phase 3 output) to produce meaningful evidence-backed
  scores — consider seeding data earlier if organic submissions are low.

## 5. Risk Register (execution-level)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM provider rate limits/cost overruns during dev | Medium | Medium | Use Ollama locally for dev/test; reserve paid providers for staging/prod |
| Schema churn late in project destabilizing embeddings | Medium | High | Freeze core `failures` schema after Week 2; use additive migrations after |
| Empty-state problem at launch (no content) | High | High | Seed with curated public postmortems by Week 7 |
| Single point of failure in solo/small team execution | Medium | High | Keep phases modular so scope can flex (e.g. defer GitHub Integration if behind schedule) |
| GitHub import extraction quality | Medium | Medium | Human-review-required draft state; schema validation with retry |

## 6. Definition of Done (v1 Launch)

- All Phase 1–8 exit criteria met.
- All NFRs from `trd.md` §7 verified under load.
- Security checklist complete (auth, RBAC, rate limiting, secret
  scanning, audit logging).
- Seed content published so search/assistant/prediction are not empty on
  day one.
- Monitoring and alerting active; on-call runbook published.
- Rollback procedure tested at least once in staging.
