# Agent Rules

This file is the short operational rulebook for AI tools working in this repo.

## Required Workflow

- Read [docs/README.md](/Users/thomasorth/case-shift/docs/README.md) and [docs/adr/README.md](/Users/thomasorth/case-shift/docs/adr/README.md) before making architectural changes.
- Prefer small, contract-preserving changes over broad refactors.
- If a change conflicts with an ADR, update the ADR in the same change or do not make the change.

## Hard Rules

- The canonical backend package namespace is `litigation_api`.
- Do not introduce or restore imports rooted at `app`.
- The canonical normalization module path is `litigation_api.ingestion`.
- Do not create or use a top-level `ingestion` package unless a new ADR explicitly restores it.
- Tier 1 domain models must stay aligned with the spec in `docs/litigation-engine/falkordb_case_engine_specs/01-tier-1-foundation-spec.md`.
- Do not replace explicit identifiers like `case_id`, `entry_id`, `doc_id`, or `chunk_id` with generic `id` fields in shared domain models.
- Keep CRLCA-specific field names out of canonical domain models.
- The health endpoint contract is `GET /health`.
- Do not move health under `/api/v1` or another versioned prefix unless the docs and ADRs are updated together.
- Schema initialization must preserve lookup-path indexes, not just durable-ID indexes.

## Canonical Paths

- Backend app entrypoint: `backend/src/litigation_api/main.py`
- Domain models: `backend/src/litigation_api/models/domain.py`
- API response models: `backend/src/litigation_api/models/api.py`
- Health route: `backend/src/litigation_api/api/routes/health.py`
- Schema init: `backend/src/litigation_api/db/schema.py`
- Init script: `backend/src/litigation_api/scripts/init_db.py`
- Normalization: `backend/src/litigation_api/ingestion/normalization.py`
- CRLCA source models: `backend/src/litigation_api/ingestion/crlca_models.py`
- ADR index: `docs/adr/README.md`

## Commit Rules

- Follow Conventional Commits.
- Use commit messages like:
  - `feat: add normalization warnings`
  - `fix: preserve /health contract`
  - `docs: add ADR for schema index strategy`
  - `test: lock tier1 domain model invariants`

## PR Guardrails

- Do not silently change public endpoint paths.
- Do not silently rename canonical Tier 1 model fields.
- Do not move package boundaries without updating imports, tests, and docs in the same change.
- Add or update tests when changing contracts, schema init behavior, or package layout.
