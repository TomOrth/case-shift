# Tier 1 Spec: Searchable Case Timeline MVP

## Purpose

Build the first usable version of the Legal Case Evolution Engine on FalkorDB. This tier focuses on ingestion, graph persistence, searchable timelines, and filing retrieval.

## Success criteria

- ingest 25 to 100 cases
- persist graph entities and relationships in FalkorDB
- retrieve a case timeline in chronological order
- perform semantic search over documents and chunks
- support a basic UI for browsing cases and filings

## Scope

### In scope

- constrained ingestion pipeline
- document type normalization
- graph schema initialization
- document and chunk embedding generation
- timeline and search APIs
- minimal frontend pages

### Out of scope

- inflection-point ranking
- issue evolution detection
- graph algorithms
- production deployment automation
- cross-case trajectory similarity

## Supported document classes

The MVP should only support:

- complaint
- amended complaint
- motion to dismiss
- injunction-related motion or order
- summary judgment motion or order
- settlement agreement
- settlement approval order
- memorandum opinion or major order

## Data model

### Node labels

- Case
- DocketEntry
- Document
- Chunk
- Party
- Judge
- EventType

### Relationship types

- HAS_ENTRY
- HAS_DOCUMENT
- HAS_CHUNK
- INVOLVES_PARTY
- AUTHORED
- HAS_EVENT_TYPE
- NEXT_DOC

## Required properties

### Case

- case_id
- case_name
- court
- jurisdiction
- filed_date
- closed_date
- status

### DocketEntry

- entry_id
- case_id
- docket_number
- filed_at
- title
- entry_type
- source_url

### Document

- doc_id
- case_id
- entry_id
- document_type
- title
- filed_at
- author_type
- disposition
- summary
- summary_embedding

### Chunk

- chunk_id
- doc_id
- case_id
- chunk_index
- page_start
- page_end
- text
- embedding

## Ingestion pipeline

### Step 1: normalize metadata

Input: raw case JSON, docket data, and file references.

Output: normalized objects for case, docket entry, and document.

Requirements:

- idempotent ingestion based on source identifiers
- durable IDs for all graph nodes
- parse and normalize dates before graph write

### Step 2: parse document text

Requirements:

- preserve page ranges
- detect empty or low-quality parses
- store extracted raw text outside the graph as artifact files

### Step 3: classify document type

Use rules first, model fallback second.

Rules should examine:

- title
- first page header
- docket entry title
- keywords like complaint, order, injunction, settlement, memorandum, summary judgment

### Step 4: chunk document

Requirements:

- chunk size should balance context and retrieval quality
- preserve chunk order
- preserve page boundaries where possible
- include chunk index and page range in output

### Step 5: summarize and embed

Requirements:

- create one document-level summary
- create chunk embeddings
- create one document summary embedding

## API contract

### GET /health

Returns service health and graph connectivity.

### GET /cases/{case_id}

Returns case metadata and document counts.

### GET /cases/{case_id}/timeline

Returns ordered documents for the case.

Query params:

- top_n optional
- document_types optional

### GET /documents/{doc_id}

Returns document metadata, summary, and chunk references.

### POST /search/semantic

Request body:

```json
{
  "query": "camping enforcement injunction",
  "document_types": ["order", "motion"],
  "court": "S.D. Florida",
  "year_from": 2010,
  "top_k": 10
}
```

Behavior:

- vector search generates candidates
- filtering and reranking occur after candidate retrieval
- response includes matched document plus top supporting chunks

## Frontend requirements

### Case page

Show:

- case metadata
- ordered timeline
- document count by type

### Document page

Show:

- metadata
- summary
- chunk excerpts
- links to predecessor and successor filings if available

### Search page

Show:

- query box
- filters
- results list with score and evidence snippets

## Acceptance tests

- ingesting the same case twice does not duplicate nodes
- every Document has a Case and DocketEntry link
- every Chunk belongs to exactly one Document
- timeline ordering matches filed_at
- semantic search returns ranked results and at least one evidence chunk

## Suggested task breakdown for AI coding tools

1. create FalkorDB schema initialization module
2. implement normalized domain models
3. implement metadata ingestion
4. implement parser and chunker
5. implement embedding pipeline
6. implement graph writer repository layer
7. implement timeline API
8. implement semantic search API
9. implement minimal UI pages
10. implement integration tests
