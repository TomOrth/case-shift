from fastapi import APIRouter

from litigation_api.models.api import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Basic health check endpoint.
    """
    return HealthResponse()
