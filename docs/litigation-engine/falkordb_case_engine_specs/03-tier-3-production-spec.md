# Tier 3 Spec: Production-Grade Legal Intelligence Platform

## Purpose

Harden the system for durable operation and add cross-case retrieval, evaluation, observability, and deployment support.

## Success criteria

- repeatable deployment of API, workers, and FalkorDB
- reliable ingestion with retries and dead-letter handling
- backups and restore procedures
- observability for latency, failures, and queue lag
- cross-case similarity and trajectory retrieval
- evaluation framework for retrieval and ranking quality

## Scope

### In scope

- background job orchestration
- admin and operational endpoints
- quality evaluation scripts
- deployment manifests and runbooks
- cross-case similarity services
- caching and reranking improvements

### Out of scope

- public multi-tenant SaaS billing
- user-facing fine-tuning workflows
- collaborative annotations unless explicitly added later

## Architecture requirements

### Services

- API service
- worker service
- scheduler or batch orchestrator
- FalkorDB service
- object storage or filesystem artifact store

### Operational concerns

- idempotent ingestion
- retries with bounded backoff
- dead-letter queue for failed document jobs
- structured logging
- request tracing if practical

## Cross-case similarity

### Goal

Compare cases by major events, issue evolution, and document similarity.

### Required approaches

- case-level embedding or pooled summary representation
- event-sequence comparison
- issue overlap scoring
- optional graph-neighborhood comparison

### API additions

#### GET /cases/{case_id}/similar

Returns similar cases with similarity dimensions.

#### GET /cases/{case_id}/trajectory

Returns normalized event sequence and issue transitions.

## Evaluation framework

### Retrieval evaluation

Measure:

- precision at k
- evidence quality of returned chunks
- deduplication effectiveness

### Inflection evaluation

Measure:

- overlap with manually identified major filings
- score stability under repeated runs

### Explanation evaluation

Measure:

- presence of structured evidence
- hallucination rate based on linked graph facts

## Observability requirements

Track:

- API latency by endpoint
- graph query duration
- queue lag
- job success and failure counts
- ingestion throughput
- vector search latency
- reranking latency
- cache hit rate if caching exists

## Backup and recovery

Requirements:

- raw documents retained outside graph DB
- parsed text artifacts retained
- periodic graph backups or snapshots
- documented restore procedure

## Security and governance

Requirements:

- redact or handle sensitive document fields according to project policy
- no arbitrary Cypher execution exposed to end users
- authenticated admin endpoints
- environment-based configuration

## Deployment deliverables

- Dockerfiles for API and worker
- docker-compose for local integration
- Kubernetes manifests or Helm chart optional
- environment variable reference
- runbook for ingestion, restore, and rollback

## Acceptance tests

- failed document jobs can be retried without duplication
- system restore from backup reproduces key graph counts
- similar-case endpoint returns diversified results
- operational metrics are emitted for API and worker paths

## Suggested task breakdown for AI coding tools

1. implement worker queue and retry policy
2. add admin endpoints and health checks
3. implement cross-case similarity service
4. implement evaluation scripts
5. add metrics and structured logging
6. add backup and restore tooling
7. create deployment files and runbooks
8. create load and resilience tests
