# ADR-0005: Keep Normalization Inside the Backend Package and Avoid Standalone Ingestion Package Drift

## Status
Accepted

## Context

The repo started with a top-level `ingestion/` package, then later reorganized source code under `backend/src/litigation_api/ingestion`. During that transition, tests and imports drifted, and the normalization code temporarily depended on backend models without a clear package boundary.

## Decision

For the current repo layout, normalization code lives under `backend/src/litigation_api/ingestion/`.

CRLCA source models and normalization helpers are part of the backend package namespace for now, because they depend on the canonical Tier 1 domain models that also live there.

The old top-level `ingestion/` package should not be treated as the active source location unless a future extraction effort deliberately restores it as an independently packaged module.

## Consequences

- Tests should import normalization code from `litigation_api.ingestion.*`.
- Tooling should not generate new top-level `ingestion/` modules by default.
- If normalization is later split into a shared or standalone package, that should be done with a new ADR and an explicit dependency strategy.

## Guidance for Tools

- Assume `litigation_api.ingestion` is the canonical normalization module path.
- Do not mix `ingestion.*` and `litigation_api.ingestion.*` imports in the same codebase state.
- When moving package boundaries, update tests and import paths in the same change.
