# ADR-0002: Keep Tier 1 Domain Models Spec-Aligned and Source-Agnostic

## Status
Accepted

## Context

Earlier iterations drifted toward CRLCA-shaped placeholder models with fields like `id`, `name`, `file`, and `date`. That conflicted with the Tier 1 spec, which defines canonical graph/domain fields such as `case_id`, `entry_id`, `doc_id`, `chunk_id`, `filed_at`, and `jurisdiction`.

## Decision

The shared Tier 1 domain models must remain aligned to the project spec and independent of any single upstream source.

Examples of canonical field names:

- `Case`: `case_id`, `case_name`, `court`, `jurisdiction`, `filed_date`, `closed_date`, `status`
- `DocketEntry`: `entry_id`, `case_id`, `docket_number`, `filed_at`, `title`, `entry_type`, `source_url`
- `Document`: `doc_id`, `case_id`, `entry_id`, `document_type`, `title`, `filed_at`, `author_type`, `disposition`, `summary`, `summary_embedding`
- `Chunk`: `chunk_id`, `doc_id`, `case_id`, `chunk_index`, `page_start`, `page_end`, `text`, `embedding`

## Consequences

- CRLCA-specific field names should not appear in canonical domain models.
- Upstream source payloads must be normalized into the canonical Tier 1 shape before reaching graph-write or API layers.
- Future ingestion sources should map into the same contract rather than reshaping the backend around the source.

## Guidance for Tools

- When adding or editing shared models, check them against `docs/litigation-engine/falkordb_case_engine_specs/01-tier-1-foundation-spec.md`.
- Do not introduce generic `id` fields in place of durable explicit identifiers.
- Prefer source adapters over polluting shared models with source-specific fields.
