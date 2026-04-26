from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Tier1Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Chunk(Tier1Model):
    """Tier 1 graph-backed chunk entity."""

    chunk_id: str = Field(..., description="Durable chunk identifier")
    doc_id: str = Field(..., description="ID of the parent document")
    case_id: str = Field(..., description="ID of the owning case")
    chunk_index: int = Field(..., description="Chunk order within the document")
    page_start: Optional[int] = Field(None, description="First page covered by the chunk")
    page_end: Optional[int] = Field(None, description="Last page covered by the chunk")
    text: str = Field(..., description="Chunk text")
    embedding: Optional[List[float]] = Field(
        None, description="Vector embedding for semantic retrieval"
    )


class Document(Tier1Model):
    """Tier 1 document entity aligned to the graph schema."""

    doc_id: str = Field(..., description="Durable document identifier")
    case_id: str = Field(..., description="ID of the owning case")
    entry_id: str = Field(..., description="ID of the related docket entry")
    document_type: str = Field(..., description="Normalized document class")
    title: str = Field(..., description="Human-readable document title")
    filed_at: Optional[str] = Field(None, description="Filing date or timestamp")
    author_type: Optional[str] = Field(None, description="Normalized author classification")
    disposition: Optional[str] = Field(None, description="Disposition captured for the filing")
    summary: Optional[str] = Field(None, description="Document-level summary")
    summary_embedding: Optional[List[float]] = Field(
        None, description="Embedding derived from the document summary"
    )
    ingestion_status: Optional[str] = Field(None, description="Ingestion status")


class DocketEntry(Tier1Model):
    """Tier 1 docket entry entity aligned to the graph schema."""

    entry_id: str = Field(..., description="Durable docket entry identifier")
    case_id: str = Field(..., description="ID of the owning case")
    docket_number: Optional[str] = Field(None, description="Court-assigned docket number")
    filed_at: Optional[str] = Field(None, description="Date or timestamp filed")
    title: str = Field(..., description="Entry title")
    entry_type: Optional[str] = Field(None, description="Normalized entry classification")
    source_url: Optional[HttpUrl] = Field(None, description="Canonical source URL")


class Case(Tier1Model):
    """Tier 1 case entity aligned to the graph schema."""

    case_id: str = Field(..., description="Durable case identifier")
    case_name: str = Field(..., description="Case caption")
    court: str = Field(..., description="Court where the case was filed")
    jurisdiction: str = Field(..., description="Jurisdiction of the case")
    filed_date: Optional[str] = Field(None, description="Date the case was filed")
    closed_date: Optional[str] = Field(None, description="Date the case was closed")
    status: Optional[str] = Field(None, description="Current lifecycle status")
