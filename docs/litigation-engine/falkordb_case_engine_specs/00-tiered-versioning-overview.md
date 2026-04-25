# Legal Case Evolution Engine on FalkorDB

## Tiered versioning overview

This project should be built in three tiers. Each tier must produce a usable system. Do not treat earlier tiers as throwaway prototypes. The goal is to preserve architecture and schema continuity while increasing capability.

## Project goal

Build a graph-native legal intelligence system that models cases as connected timelines of docket entries, documents, issues, parties, judges, and outcomes. The system should support:

- timeline summarization
- inflection-point detection
- semantic retrieval over filings
- issue evolution tracking
- similar-case and similar-trajectory retrieval

## Core technology choices

- Graph database: FalkorDB
- API: FastAPI
- Background jobs: Celery, Dramatiq, or Arq
- Parsing/OCR: Python-based parsing pipeline
- Embeddings: sentence-transformer class model for MVP
- Frontend: Next.js or lightweight React client
- Storage outside graph DB: object storage or filesystem for raw PDFs and parsed artifacts

## Why tiered development

The project has three hard parts:

1. document ingestion and normalization
2. graph modeling and query behavior
3. legal-domain reasoning over time

Trying to solve all three at once will create a vague, unstable system. Each tier should narrow uncertainty.

---

## Tier 1: Searchable case timeline MVP

### Objective

Build a working graph-backed system that ingests cases and exposes searchable timelines and filing-level semantic retrieval.

### User value

A user can open a case, inspect major filings, and search for semantically similar documents.

### What must exist

- FalkorDB schema
- ingestion pipeline for a constrained document set
- document and chunk embeddings
- timeline API
- semantic search API
- minimal case UI

### What is explicitly out of scope

- trajectory similarity across cases
- advanced issue evolution
- graph centrality scoring
- production multi-tenancy
- online learning or automatic relabeling

### Exit criteria

Tier 1 is complete when a user can ingest 25 to 100 cases and perform case timeline retrieval plus filing-level semantic search with acceptable latency.

---

## Tier 2: Evolution and inflection intelligence

### Objective

Add legal reasoning features that identify major changes in case trajectory and explain why filings matter.

### User value

A user can see major inflection points, issue shifts, and structured explanations of why a filing is important in context.

### What must exist

- issue extraction
- event-type tagging
- inflection scoring
- document-to-document reference edges
- document explanation endpoint
- richer case UI with issue and event views

### What is explicitly out of scope

- full production replication strategy
- tenant isolation
- advanced compliance and admin tooling

### Exit criteria

Tier 2 is complete when the system can rank likely inflection points in a case and produce evidence-grounded explanations using graph context.

---

## Tier 3: Production-grade legal intelligence platform

### Objective

Harden the system for real operational use and add cross-case trajectory retrieval and deployment-grade observability.

### User value

A user can run the system at larger scale, compare cases by trajectory, and operate the platform with repeatable ingestion, monitoring, and recovery.

### What must exist

- multi-stage background processing
- snapshot and backup strategy
- observability and admin endpoints
- cross-case similarity service
- reranking and quality evaluation
- deployment manifests and runbooks

### Exit criteria

Tier 3 is complete when the system is deployable as a stable internal platform and supports repeatable ingestion, search, timeline analysis, and trajectory comparison.

---

## Recommended build order

1. Tier 1 schema and ingestion
2. Tier 1 APIs and minimal UI
3. Tier 2 issue extraction and event modeling
4. Tier 2 inflection scoring and explanations
5. Tier 3 production hardening and similarity services

## Design constraints

- The graph schema must remain stable across tiers.
- Node identifiers must be durable and externalized.
- All LLM use must be optional or replaceable.
- Retrieval must use two-stage ranking when vector plus structured filtering is needed.
- Raw source documents must remain outside the graph database and be referenced by URI.

## AI-assisted development guidance

When using AI coding tools:

- assign one tier at a time
- require generated code to conform to the schema and API contracts in the spec files
- avoid asking the model to invent new entities outside the defined ontology
- require tests and acceptance checks for each task
- do not allow generated code to skip idempotency, deduplication, or structured logging
