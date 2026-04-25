# v1 Ingestion Contract & Document Taxonomy

This document defines the input contract and supported document taxonomy for the v1 ingestion pipeline. To ensure stability and testability for the MVP, we are building against a single, explicit source target.

## 1. Launch Corpus Source

For the v1 launch, the sole supported source for ingestion is the **Civil Rights Litigation Clearinghouse API (CRLCA)**.

*   **API Version:** V2.1
*   **Base URL:** `https://clearinghouse.net/api/v2p1/`

## 2. Ingestion Input Contract

The ingestion pipeline will map incoming CRLCA JSON objects to our internal representations. To ensure idempotent ingestion and stable references, the following fields are required or optional.

### 2.1. Case Mapping
Maps from the CRLCA `Case` object.

**Required Fields:**
*   `id` (integer): The unique source identifier for the case. Used as the primary key/reference for idempotency.
*   `name` (string): The title/name of the case.
*   `court` (string): The court where the case was filed.

**Optional/Mapped Fields:**
*   `docket_status` (string): Status of the case docket.
*   `case_status` (string): CRLCA internal status of the case metadata.
*   `filing_date` (string): Date the case was filed (YYYY-MM-DD).
*   `summary` (string): Summary description of the case.

### 2.2. Docket Mapping
Maps from the CRLCA `Docket` or `main_docket` object nested inside a Case.

**Required Fields:**
*   `id` (integer): Unique docket identifier.
*   `docket_number_manual` or `docket_filing_number` (string/number): The actual court docket number.

**Optional Fields:**
*   `date_filed` (string): Filing date.

### 2.3. Document Mapping
Maps from the CRLCA `Document` object.

**Required Fields:**
*   `id` (integer): Unique identifier for the document.
*   `title` or `description` (string): Human-readable name for the document.
*   `file` (string): URL to the actual PDF file for download.
*   `document_type` (string): The category of the document (must map to our taxonomy).

**Optional Fields:**
*   `date` (string): Date the document was filed/signed.
*   `ecf_number` (string): PACER/ECF number for the document.

## 3. Supported Document Taxonomy (Tier 1)

For v1, the worker pipeline (OCR, parsing, Kanon 2 Embedder) will only process specific types of documents. We map the CRLCA `document_type` directly to our supported classes.

**Supported Document Classes:**
1.  **Complaint**: Maps from CRLCA `"Complaint"`.
2.  **Opinion/Order**: Maps from CRLCA `"Opinion/Order"`.
3.  **Settlement**: Maps from CRLCA `"Settlement"`.

Documents matching these exact strings in the CRLCA `document_type` field will be fully downloaded, parsed, and indexed into the graph.

## 4. Unsupported Document Fallback Behavior

Any document fetched from the CRLCA where the `document_type` does not match the Tier 1 Supported Document Classes (e.g., "Correspondence", "Transcripts", "Legislative Report", or `null`) will be handled as follows:

1.  **Metadata Only:** The document's metadata (ID, title, date) will be recorded in the internal database and attached to the parent Case node.
2.  **No Artifact Download:** The raw PDF file will **not** be downloaded from the `file` URL to save bandwidth and storage.
3.  **No Processing:** The document will **not** be queued for the worker. No OCR, text extraction, or embedding will occur.
4.  **Status Marking:** The internal representation of the document will be marked with a status of `SKIPPED_UNSUPPORTED_TYPE`.