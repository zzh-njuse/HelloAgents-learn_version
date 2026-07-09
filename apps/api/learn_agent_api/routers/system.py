from fastapi import APIRouter, Depends

from learn_agent_api.settings import Settings, get_settings

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/info")
def system_info(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "database": {"configured": bool(settings.database_url)},
        "qdrant": {"configured": bool(settings.qdrant_url)},
        "redis": {"configured": bool(settings.redis_url)},
        "storage": {"configured": bool(settings.storage_root)},
    }
