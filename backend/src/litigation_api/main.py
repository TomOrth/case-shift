from fastapi import FastAPI

from litigation_api.api.routes import health
from litigation_api.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Case Shift API",
        version="0.1.0",
    )

    app.include_router(health.router)

    return app

app = create_app()
