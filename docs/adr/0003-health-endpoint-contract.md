# ADR-0003: Preserve the Unversioned `GET /health` Contract

## Status
Accepted

## Context

The Tier 1 spec and development rules define a `GET /health` endpoint. A previous implementation mounted the health router under `/api/v1`, which changed the externally documented path to `/api/v1/health` and broke the contract.

## Decision

The health check endpoint path is `GET /health`.

It is intentionally unversioned unless a future ADR explicitly changes the API versioning strategy for infrastructure endpoints.

## Consequences

- Backend routing should expose `/health` exactly.
- Tests and smoke checks should assert `/health`, not `/api/v1/health`.
- If a versioned API namespace is introduced for business endpoints, health remains outside that namespace by default.

## Guidance for Tools

- Do not move health under `/api/v1` or another prefix unless the docs and ADRs are updated together.
- Treat this as a compatibility-sensitive endpoint used by local tooling and deploy checks.
