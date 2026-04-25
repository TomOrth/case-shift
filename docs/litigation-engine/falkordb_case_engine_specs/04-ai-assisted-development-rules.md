# AI-Assisted Development Rules for the Legal Case Evolution Engine

## Purpose

Use this file as the instruction context for coding assistants. It defines how generated code should behave and what assumptions are allowed.

## System boundaries

The project is a graph-native legal intelligence system built on FalkorDB. The assistant must not replace the graph model with a relational-only or vector-only design.

## Non-negotiable design rules

- Preserve the defined node labels and relationship types.
- Preserve durable external IDs for all graph entities.
- Use idempotent upserts for ingestion.
- Keep raw source documents outside the graph database.
- Use two-stage retrieval when vector search and structured filtering are both required.
- Keep LLM dependencies optional and behind interfaces.
- Prefer deterministic rules before model calls when classifying document types or event types.
- Do not expose arbitrary graph query execution to user-facing APIs.

## Coding rules

- Use Python type hints.
- Use Pydantic models for API contracts.
- Use repository or service boundaries instead of mixing Cypher directly into route handlers.
- Add structured logging for ingestion and query operations.
- Add unit tests for scoring and extraction logic.
- Add integration tests for graph write and read paths.
- Make repeated ingestion safe.

## Schema contract

### Node labels

- Case
- DocketEntry
- Document
- Chunk
- Issue
- Party
- Judge
- EventType

### Relationship types

- HAS_ENTRY
- HAS_DOCUMENT
- HAS_CHUNK
- ASSERTS_ISSUE
- INVOLVES_PARTY
- AUTHORED
- NEXT_DOC
- REFERS_TO
- RESOLVES
- HAS_EVENT_TYPE
- SIMILAR_DOC optional

## API contract expectations

The assistant must preserve endpoint names and response semantics defined in the tier specs unless explicitly told to version them.

## Performance expectations

- Avoid N+1 graph query patterns.
- Batch writes where practical.
- Rerank search results after vector candidate retrieval.
- Keep document explanations grounded in linked graph evidence.

## Forbidden shortcuts

- Do not store only flattened JSON blobs instead of graph entities.
- Do not skip deduplication because the seed dataset is small.
- Do not hardcode a single court or case into production code.
- Do not embed business logic only inside prompts.
- Do not return explanations without evidence references.

## Task prompt template for coding assistants

Use the following structure when asking an AI assistant to implement a task:

1. objective
2. relevant tier
3. files allowed to change
4. schema entities involved
5. API contracts involved
6. acceptance criteria
7. test requirements
8. constraints and forbidden changes

## Example task prompt

Objective: implement the Tier 1 timeline endpoint.
Relevant tier: Tier 1.
Files allowed to change: apps/api/routes/cases.py, apps/api/services/timeline_service.py, apps/api/db/repository.py, tests/integration/test_timeline_api.py.
Schema entities involved: Case, DocketEntry, Document, NEXT_DOC.
Acceptance criteria: returns ordered documents for a case, supports optional top_n, excludes duplicates, includes doc_id, title, document_type, filed_at, summary.
Test requirements: integration test with seeded graph.
Constraints: do not change endpoint path, do not put Cypher directly inside route handler, do not introduce ORM.
