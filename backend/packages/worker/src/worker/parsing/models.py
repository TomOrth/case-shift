from typing import List, Optional
from pydantic import BaseModel, Field

class ParsedPage(BaseModel):
    page_number: int = Field(..., description="The original page number")
    text: str = Field(..., description="Extracted text from the page")
    is_blank: bool = Field(False, description="Whether the page was intentionally blank")

class ParsedArtifact(BaseModel):
    doc_id: str = Field(..., description="Identifier matching the Tier 1 Document doc_id")
    pages: List[ParsedPage] = Field(default_factory=list, description="Text broken down by page")
    total_pages: int = Field(0, description="Total number of parsed pages")
    is_low_quality: bool = Field(False, description="Flag indicating poor OCR or extraction quality")
    is_empty: bool = Field(False, description="Flag indicating no text was recovered")
