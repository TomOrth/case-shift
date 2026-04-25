from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import health

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Case Shift API",
        version="0.1.0",
    )

    app.include_router(health.router, prefix="/api/v1")

    return app

app = create_app()
