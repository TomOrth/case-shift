from typing import Optional, Union, Any
from pydantic import BaseModel, Field

class CRLCADocument(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    file: str
    document_type: Optional[str] = None
    date: Optional[str] = None
    ecf_number: Optional[str] = None

class CRLCADocket(BaseModel):
    id: int
    docket_number_manual: Optional[Union[str, int]] = None
    docket_filing_number: Optional[Union[str, int]] = None
    date_filed: Optional[str] = None

class CRLCACase(BaseModel):
    id: int
    name: str
    court: str
    docket_status: Optional[str] = None
    case_status: Optional[str] = None
    filing_date: Optional[str] = None
    summary: Optional[str] = None
