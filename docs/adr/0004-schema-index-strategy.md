# ADR-0004: Create Schema Indexes for Lookup Paths, Not Just Durable IDs

## Status
Accepted

## Context

Issue `#4` is not just about creating any indexes; it explicitly requires query-supporting indexes for case, document, and timeline retrieval paths. A durable-ID-only strategy leaves common Tier 1 queries unindexed and shifts the performance problem into later PRs.

## Decision

Schema initialization must create indexes for both:

1. durable identifiers, and
2. the core Tier 1 lookup paths used by timeline/document retrieval

Current expected index coverage includes:

- `Case.case_id`
- `DocketEntry.entry_id`, `DocketEntry.case_id`, `DocketEntry.filed_at`
- `Document.doc_id`, `Document.case_id`, `Document.entry_id`, `Document.filed_at`
- `Chunk.chunk_id`, `Chunk.doc_id`, `Chunk.case_id`
- `Party.party_id`
- `Judge.judge_id`
- `EventType.event_type_id`

## Consequences

- Schema init should not be reduced to primary-ID indexing only.
- New query paths should prompt an ADR update or schema index review if they become part of Tier 1 guarantees.
- Schema init should remain repeatable and safe to rerun.

## Guidance for Tools

- When editing schema init, preserve the existing lookup-path indexes unless there is a deliberate replacement strategy.
- Avoid suggesting “we can index that later” for Tier 1 retrieval paths already committed in the backlog.
