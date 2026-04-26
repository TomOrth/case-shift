# Classification Fallback Behavior

This document outlines the rules-first approach and explicit fallback behavior used by the ingestion pipeline to classify documents into the Tier 1 taxonomy.

## 1. Goal

The Tier 1 taxonomy specifically supports the following document types for ingestion and downstream processing (e.g., OCR, embedding, tracking):

*   **Complaint**
*   **Opinion/Order**
*   **Settlement**

All incoming documents from the Civil Rights Litigation Clearinghouse API (CRLCA) or other sources must be assigned to one of these types or gracefully marked as `"Unknown"` if unsupported.

## 2. Order of Precedence

The classification module evaluates a document in the following deterministic order:

### 2.1. Exact Match
If the source payload explicitly lists a `document_type` that exactly matches `Complaint`, `Opinion/Order`, or `Settlement`, that classification is used immediately.

### 2.2. Deterministic Heuristics
If there is no exact match, the system falls back to regex-based heuristics against the available fields, evaluated in this order:
1.  `document_type`
2.  `title`
3.  `docket_title`

Keywords evaluated (case-insensitive):
*   **Complaint:** `\bcomplaint\b`
*   **Opinion/Order:** `\b(opinion|order|decision|ruling)\b`
*   **Settlement:** `\b(settlement|consent decree|stipulation|agreement)\b`

### 2.3. Optional AI Fallback Interface
An optional interface, `ClassificationProvider`, is provided to support future model-assisted classification. If injected, this provider will receive the document's text and titles to make a prediction. This is out of scope for the current Tier 1 implementation but remains an open integration point.

### 2.4. Explicit Fallback ("Unknown")
If all the steps above fail to classify the document, it is explicitly classified as `"Unknown"`.

## 3. Handling "Unknown" Documents

Documents classified as `"Unknown"` will not break the ingestion pipeline. According to the fallback behavior specified in the v1 Ingestion Contract:

*   **Metadata Only:** The document's basic metadata is extracted and saved to the graph.
*   **No Artifact Download:** The raw PDF file will **not** be downloaded, saving bandwidth and storage.
*   **Status Update:** The internal representation of the document will have its `ingestion_status` marked as `SKIPPED_UNSUPPORTED_TYPE`.
