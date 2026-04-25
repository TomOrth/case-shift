# Repo Map

This is a quick navigation guide for humans and tools.

## Core Backend

- App entrypoint: [backend/src/litigation_api/main.py](/Users/thomasorth/case-shift/backend/src/litigation_api/main.py)
- Config: [backend/src/litigation_api/core/config.py](/Users/thomasorth/case-shift/backend/src/litigation_api/core/config.py)
- Health route: [backend/src/litigation_api/api/routes/health.py](/Users/thomasorth/case-shift/backend/src/litigation_api/api/routes/health.py)
- Domain models: [backend/src/litigation_api/models/domain.py](/Users/thomasorth/case-shift/backend/src/litigation_api/models/domain.py)
- API models: [backend/src/litigation_api/models/api.py](/Users/thomasorth/case-shift/backend/src/litigation_api/models/api.py)
- Schema init: [backend/src/litigation_api/db/schema.py](/Users/thomasorth/case-shift/backend/src/litigation_api/db/schema.py)
- DB init script: [backend/src/litigation_api/scripts/init_db.py](/Users/thomasorth/case-shift/backend/src/litigation_api/scripts/init_db.py)

## Ingestion and Normalization

- CRLCA source models: [backend/src/litigation_api/ingestion/crlca_models.py](/Users/thomasorth/case-shift/backend/src/litigation_api/ingestion/crlca_models.py)
- Normalization logic: [backend/src/litigation_api/ingestion/normalization.py](/Users/thomasorth/case-shift/backend/src/litigation_api/ingestion/normalization.py)

## Tests

- Test bootstrap: [backend/tests/conftest.py](/Users/thomasorth/case-shift/backend/tests/conftest.py)
- API tests: [backend/tests/test_api.py](/Users/thomasorth/case-shift/backend/tests/test_api.py)
- Config tests: [backend/tests/test_config.py](/Users/thomasorth/case-shift/backend/tests/test_config.py)
- Model tests: [backend/tests/test_models.py](/Users/thomasorth/case-shift/backend/tests/test_models.py)
- Schema tests: [backend/tests/test_schema.py](/Users/thomasorth/case-shift/backend/tests/test_schema.py)
- Normalization tests: [backend/tests/test_normalization.py](/Users/thomasorth/case-shift/backend/tests/test_normalization.py)

## Decision Sources

- ADR index: [docs/adr/README.md](/Users/thomasorth/case-shift/docs/adr/README.md)
- Architecture overview: [docs/architecture.md](/Users/thomasorth/case-shift/docs/architecture.md)
- Ingestion contract: [docs/ingestion_contract_v1.md](/Users/thomasorth/case-shift/docs/ingestion_contract_v1.md)
- Tier 1 spec: [docs/litigation-engine/falkordb_case_engine_specs/01-tier-1-foundation-spec.md](/Users/thomasorth/case-shift/docs/litigation-engine/falkordb_case_engine_specs/01-tier-1-foundation-spec.md)

## If You Are Changing...

- Package layout or imports: update source imports, tests, and ADRs together.
- Tier 1 models: update the spec-aligned domain model tests and check ADR-0002.
- Health endpoint: check ADR-0003 before changing anything.
- Schema init or indexes: check ADR-0004 and update schema tests.
- Normalization boundaries: check ADR-0005 and keep imports under `litigation_api.ingestion`.
