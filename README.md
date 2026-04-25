# case-shift

A graph-native litigation intelligence engine for tracking, visualizing, and querying civil rights court cases.

## The core idea

A lawsuit is not a flat list of documents. It is a timeline of interconnected events — filings, motions, orders, and decisions — each one capable of shifting the trajectory of the case. A complaint sets the legal theory. A motion to dismiss tests it. An injunction changes the stakes. A settlement ends it. The path between those moments is what case-shift is built to surface.

Most legal research tools treat a case as a document collection. case-shift treats it as a graph: a network of nodes (filings, parties, judges, events) connected by edges that encode sequence, causation, and legal relationship. That structure makes it possible to ask questions that keyword search cannot answer:

- What were the major inflection points in this case?
- Which filings preceded a significant outcome like a settlement or dismissal?
- What issues evolved across the docket over time?
- Which other cases followed a similar trajectory?
- What did the court say about a specific legal issue across all filings?

The name reflects this: cases shift. The graph captures how and why.

## Data source

The v1 launch corpus is the **Civil Rights Litigation Clearinghouse API (CRLCA)** at `https://clearinghouse.net/api/v2p1/`. This provides structured case metadata, docket entries, and document references for civil rights litigation across federal courts.

## Graph model

Cases are stored in **FalkorDB** as a property graph. The core node types are:

- `Case` — top-level case with court, jurisdiction, status, and dates
- `DocketEntry` — individual docket filings linked to a case
- `Document` — parsed court documents (complaints, orders, settlements, etc.)
- `Chunk` — text segments of documents with vector embeddings for semantic search
- `Party` — plaintiffs, defendants, and intervenors
- `Judge` — presiding judges
- `EventType` — structured event labels attached to filings

Relationships like `HAS_ENTRY`, `HAS_DOCUMENT`, `HAS_CHUNK`, `INVOLVES_PARTY`, `AUTHORED`, and `NEXT_DOC` connect these nodes into a traversable case timeline.

The graph schema is designed to be stable across all three development tiers. Node identifiers are durable and externalized. Raw source documents live outside the graph and are referenced by URI.

## What you can ask the graph

**Tier 1 (current):** Timeline and semantic retrieval
- Show me all filings in this case in chronological order
- Find documents semantically similar to this query across all cases
- What complaints and orders exist for this case?

**Tier 2 (planned):** Inflection and evolution intelligence
- What were the turning points in this case?
- How did the legal issues shift between the complaint and the final order?
- Which filing most changed the trajectory of the case?

**Tier 3 (planned):** Cross-case trajectory analysis
- Which other cases followed a similar arc — complaint → injunction → settlement?
- What patterns appear across civil rights cases in this jurisdiction?

## Architecture

The system is a monorepo with four domains:

```
case-shift/
├── backend/      # FastAPI — graph queries, timeline API, semantic search
├── frontend/     # Next.js — case browser, timeline view, search UI
├── worker/       # ARQ (async Redis queue) — OCR, parsing, embedding jobs
└── ingestion/    # CRLCA pipeline — fetch, normalize, queue for processing
```

**Ingestion flow:**

```
CRLCA API → source models → normalization → Tier 1 domain models → FalkorDB graph
```

Raw PDFs are stored in S3-compatible object storage (`/raw/`) and parsed artifacts in `/parsed/`. The graph holds metadata, summaries, and embeddings — not raw file content.

**Document processing** (handled by the worker):
1. Fetch and sanitize raw documents from CRLCA
2. Parse text with page-range preservation
3. Classify document type (complaint, order, settlement, etc.)
4. Chunk text for retrieval
5. Embed chunks and document summaries using the **Kanon 2 Embedder** (legal-domain embedding model)
6. Write nodes and edges to FalkorDB

## Development tiers

The system is built in three tiers, each producing a usable product:

**Tier 1 (current):** Searchable case timeline MVP — ingest 25–100 cases, browse timelines, semantic search over filings.

**Tier 2:** Evolution and inflection intelligence — issue extraction, event-type tagging, inflection-point scoring, document-to-document reference edges.

**Tier 3:** Production-grade platform — cross-case trajectory similarity, multi-stage processing, observability, deployment runbooks.

## Stack

| Layer | Technology |
|---|---|
| Graph DB | FalkorDB |
| Backend API | FastAPI (Python) |
| Background jobs | ARQ + Redis |
| Embeddings | Kanon 2 Embedder |
| Frontend | Next.js |
| Blob storage | S3-compatible (LocalStack for local dev) |
| Config | pydantic-settings |

## Local setup

```bash
# Backend
cd backend
uv sync
uv run uvicorn src.litigation_api.main:app --reload

# Run tests
uv run pytest
```

See `docs/architecture.md` for full system design decisions and `docs/ingestion_contract_v1.md` for the CRLCA field mapping spec.
