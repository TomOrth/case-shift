from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import date

class Chunk(BaseModel):
    """
    Represents a chunk of text parsed from a Document for vectorizing.
    """
    id: str = Field(..., description="Unique identifier for the chunk")
    document_id: str = Field(..., description="ID of the parent Document")
    text: str = Field(..., description="The chunk text")
    page_number: Optional[int] = Field(None, description="Page number where this chunk is located")

class Document(BaseModel):
    """
    Represents a legal document (e.g., Complaint, Opinion/Order, Settlement).
    Maps from the CRLCA Document object.
    """
    id: int = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Human-readable name for the document")
    file: HttpUrl = Field(..., description="URL to the actual PDF file for download")
    document_type: str = Field(..., description="The category of the document")
    date: Optional[str] = Field(None, description="Date the document was filed/signed")
    ecf_number: Optional[str] = Field(None, description="PACER/ECF number for the document")
    chunks: List[Chunk] = Field(default_factory=list, description="Text chunks associated with the document")

class DocketEntry(BaseModel):
    """
    Represents a docket entry. Maps from the CRLCA Docket or main_docket object.
    """
    id: int = Field(..., description="Unique docket identifier")
    docket_number_manual: Optional[str] = Field(None, description="The actual court docket number")
    date_filed: Optional[str] = Field(None, description="Filing date")

class Case(BaseModel):
    """
    Represents a court case. Maps from the CRLCA Case object.
    """
    id: int = Field(..., description="The unique source identifier for the case")
    name: str = Field(..., description="The title/name of the case")
    court: str = Field(..., description="The court where the case was filed")
    docket_status: Optional[str] = Field(None, description="Status of the case docket")
    case_status: Optional[str] = Field(None, description="CRLCA internal status of the case metadata")
    filing_date: Optional[str] = Field(None, description="Date the case was filed (YYYY-MM-DD)")
    summary: Optional[str] = Field(None, description="Summary description of the case")
    docket_entries: List[DocketEntry] = Field(default_factory=list, description="Docket entries associated with the case")
    documents: List[Document] = Field(default_factory=list, description="Documents associated with the case")
