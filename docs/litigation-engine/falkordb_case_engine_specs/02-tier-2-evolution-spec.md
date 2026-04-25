# Tier 2 Spec: Evolution and Inflection Intelligence

## Purpose

Extend the Tier 1 system so it can identify major case shifts, model issue evolution, and explain why filings matter.

## Success criteria

- rank likely inflection points within a case
- extract and attach issues to documents
- create reference and resolution edges between related filings
- explain filing importance using graph context
- expose issue and event views in the UI

## Scope

### In scope

- Issue nodes and issue extraction
- inflection scoring
- document reference edges
- resolution edges from orders to motions
- explanation service
- event-type taxonomy refinement

### Out of scope

- full production deployment automation
- multi-tenant platform administration
- end-user annotation workflows

## Expanded data model

### Add node label

- Issue
n
### Add relationship types

- ASSERTS_ISSUE
- REFERS_TO
- RESOLVES
- SIMILAR_DOC optional if precomputed

## New required properties

### Document

Add:

- semantic_novelty
- inflection_score
- importance_score optional if kept distinct

### Issue

- issue_id
- label
- description
- embedding

### ASSERTS_ISSUE relationship

- confidence

### REFERS_TO relationship

- reference_type
- confidence

### RESOLVES relationship

- disposition
- confidence

## Domain logic

### Issue extraction

Each supported document may assert zero or more issues.

Candidate issue families:

- constitutional claim
- injunction request
- class certification
- municipal enforcement
- settlement enforcement
- compliance and monitoring
- fees and costs
- appeal
- stay
- policy adoption

Requirements:

- rules-first extraction for obvious labels
- model-assisted extraction for ambiguous cases
- deduplicate semantically equivalent issues

### Event typing

Each major document should have at least one EventType attached.

Examples:

- complaint_filed
- amended_complaint_filed
- motion_to_dismiss_filed
- motion_to_dismiss_denied
- injunction_requested
- injunction_granted
- settlement_proposed
- settlement_approved
- appeal_noticed
- stay_entered

### Reference edge creation

Infer document references using:

- explicit docket number mentions
- title similarity
- order text referring to specific motions
- semantic similarity constrained to same case

### Resolution edge creation

Identify when a document resolves another document.

Typical pairings:

- order resolves motion to dismiss
- order resolves injunction motion
- order approves settlement agreement
- order appoints monitor or master

## Inflection scoring

### Goal

Estimate whether a filing materially changed the case trajectory.

### Initial scoring formula

```text
inflection_score =
  0.30 * event_type_weight
+ 0.20 * semantic_novelty
+ 0.15 * issue_delta_score
+ 0.15 * future_reference_score
+ 0.10 * disposition_weight
+ 0.10 * graph_centrality_score
```

### Required score components

- event_type_weight
- semantic_novelty
- issue_delta_score
- future_reference_score
- disposition_weight
- graph_centrality_score

### Explainability requirement

The system must retain component scores so the explanation layer can show why a filing ranked highly.

## API contract additions

### GET /cases/{case_id}/inflection-points

Returns top-ranked filings with score breakdown.

### GET /cases/{case_id}/issues

Returns major issues in the case and linked filings.

### GET /documents/{doc_id}/explain

Returns:

- why this filing matters
- what issues it introduced or resolved
- what changed after it
- which later filings refer back to it

## UI additions

### Inflection view

Show:

- top inflection filings
- score breakdown
- supporting evidence

### Issue evolution view

Show:

- issues in the case
- first and last appearance
- linked filings over time

### Document explanation panel

Show:

- generated explanation
- structured evidence items
- linked prior and later filings

## Acceptance tests

- a major order can be linked to the motion it resolves
- issue extraction does not create duplicate issue nodes for identical labels
- inflection endpoint returns ranked filings with non-empty score components
- explanation endpoint cites graph evidence, not only free-form prose

## Suggested task breakdown for AI coding tools

1. add Issue schema and indexes
2. implement issue extraction pipeline
3. implement reference edge generation
4. implement resolution matching
5. implement inflection score computation
6. implement explanation service
7. add inflection and issue APIs
8. add UI views and tests
