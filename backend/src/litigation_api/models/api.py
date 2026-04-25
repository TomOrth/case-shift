from pydantic import BaseModel, Field
from typing import List, Generic, TypeVar, Optional

from litigation_api.models.domain import Case, Document, DocketEntry

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    """
    Standard envelope for API responses.
    """
    data: Optional[T] = None
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    """
    Standard envelope for API errors.
    """
    success: bool = False
    message: str
    code: Optional[int] = None

class PaginatedResponse(BaseResponse[List[T]]):
    """
    Standard envelope for paginated API responses.
    """
    total: int = 0
    page: int = 1
    size: int = 20

# Specific Tier 1 Response Models
class CaseResponse(BaseResponse[Case]):
    pass

class CasesListResponse(PaginatedResponse[Case]):
    pass

class DocumentResponse(BaseResponse[Document]):
    pass

class DocumentsListResponse(PaginatedResponse[Document]):
    pass

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
