from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from learn_agent_api.observability.logging import RequestIdMiddleware, configure_logging
from learn_agent_api.routers import health, system, workspaces
from learn_agent_api.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()

    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(RequestIdMiddleware, settings=settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(system.router)
    app.include_router(workspaces.router)
    return app


app = create_app()
