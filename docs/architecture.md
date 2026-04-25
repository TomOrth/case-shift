# v1 Architecture & Decisions

## 1. System Boundaries

The application is divided into four main domains to ensure separation of concerns and allow independent scaling:

*   **Frontend**: Next.js application responsible for the user interface, routing, and client-side rendering. It interacts exclusively with the Backend API and does not directly access databases or blob storage.
*   **Backend**: FastAPI application serving as the core API layer. It manages business logic, user authentication, and provides endpoints for the frontend. It is the primary interface to the FalkorDB graph database and the task queue.
*   **Worker**: Asynchronous background job processor. Handles computationally heavy or long-running tasks such as parsing court documents, performing OCR, running LLM extraction jobs, vectorizing text using the **Kanon 2 Embedder** (the best-in-class legal embedding model), and complex graph updates.
*   **Ingestion**: Dedicated pipeline for fetching external data (e.g., court APIs, scrapers). Specifically, it will integrate with the Civil Rights Litigation Clearinghouse API (CRLCA - `https://api.clearinghouse.net/`) to fetch civil rights litigation information and documents. It downloads raw documents, performs initial sanitization, and queues processing tasks for the Worker.

## 2. Worker Framework Decision

**Selected Framework**: ARQ (Asyncio Redis Queue)

**Justification**:
*   **Async-Native**: Since the backend is built with FastAPI (which is async-first), using ARQ allows us to share async code, database connections, and utility functions seamlessly between the backend and the worker.
*   **Lightweight**: ARQ is significantly lighter than Celery, avoiding the complex configuration overhead while still providing the reliability needed for v1.
*   **Redis Integration**: It uses Redis as the broker, which is standard, easy to host, and performant.

## 3. Storage Strategy

### 3.1. Artifact and Blob Storage
*   **Solution**: S3-compatible object storage (e.g., AWS S3 in production, LocalStack for local development).
*   **Layout Convention**:
    *   `/raw/`: Immutable storage for original downloaded documents (PDFs, Word docs). Grouped by source and date (e.g., `/raw/{source}/{YYYY}/{MM}/{DD}/{doc_id}.pdf`).
    *   `/parsed/`: Processed artifacts, such as extracted text, JSON representations, or OCR outputs (e.g., `/parsed/{doc_id}/v1_text.txt`).

### 3.2. Data and Graph Storage
*   **Graph Database**: FalkorDB will serve as the primary database for tracking relationships between cases, entities, and documents, enabling the "Litigation Engine to graph and track court cases" functionality.

## 4. Configuration and Environment Variables
*   **Python Components (Backend, Worker, Ingestion)**: Will use `pydantic-settings` to strictly validate environment variables at startup. Configuration will be loaded from a central `.env` file during development.
*   **Frontend**: Next.js standard environment variables (`.env.local` for development, injected at build/runtime in production).

## 5. Repository Layout
A monorepo structure will be used for v1 to accelerate initial development and simplify CI/CD:
```
case-shift/
├── backend/      # FastAPI application
├── frontend/     # Next.js application
├── worker/       # ARQ worker definitions and tasks
├── ingestion/    # Data fetching and scraping pipelines
└── docs/         # Architecture and project documentation
```

## 6. Model Layer Boundaries

To avoid coupling the whole system to a single upstream API, v1 will keep source-specific models separate from the canonical Tier 1 contract.

### 6.1. Canonical Domain Models
The shared models used by the backend, worker, and graph-writing code must match the Tier 1 spec exactly. These are the internal contract for the system and should use the project field names such as:

*   `case_id`, `case_name`
*   `entry_id`, `docket_number`
*   `doc_id`, `filed_at`
*   `chunk_id`, `chunk_index`, `page_start`, `page_end`

These models belong in the shared domain layer and should not contain CRLCA-specific field names like `name`, `file`, `date`, `docket_status`, or `docket_number_manual`.

### 6.2. Source-Specific Models
Any raw fields that come from the Civil Rights Litigation Clearinghouse API should live in ingestion-layer source models such as `crlca_models.py` or a similar source-specific module. Those models are allowed to mirror the upstream API exactly so ingestion can parse responses without losing fidelity.

### 6.3. Normalization Layer
Normalization code should map source-specific models into the canonical Tier 1 domain models before data reaches the backend service layer, graph repositories, or API response shaping.

The intended flow is:

`CRLCA payload -> source model -> normalization -> Tier 1 domain model -> graph/API`

### 6.4. Preserving Source Metadata
If we need upstream-only fields for idempotency, provenance, or debugging, preserve them explicitly in source adapters or a narrow provenance structure. Do not expand the canonical Tier 1 models with CRLCA-only fields unless the project spec adopts them as stable cross-source concepts.
