# Architecture Decision Records

This directory captures short, stable decisions that other tools and contributors should treat as source-of-truth defaults when working in this repo.

## ADR Index

- [ADR-0001: Use `litigation_api` as the canonical backend package namespace](./0001-backend-package-namespace.md)
- [ADR-0002: Keep Tier 1 domain models spec-aligned and source-agnostic](./0002-tier1-domain-model-contract.md)
- [ADR-0003: Preserve the unversioned `GET /health` contract](./0003-health-endpoint-contract.md)
- [ADR-0004: Create schema indexes for lookup paths, not just durable IDs](./0004-schema-index-strategy.md)
- [ADR-0005: Keep normalization inside the backend package and avoid standalone ingestion package drift](./0005-normalization-module-boundary.md)

## How to Use These ADRs

- Prefer these decisions over older paths, placeholder code, or generated code suggestions.
- If a tool proposes a conflicting change, update the ADR first or explain why the ADR no longer applies.
- If a decision becomes obsolete, add a new ADR that supersedes the old one rather than silently drifting.
