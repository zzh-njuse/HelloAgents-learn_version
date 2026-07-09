from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from urllib.parse import urlparse

import redis
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from learn_agent_api.db.session import get_db
from learn_agent_api.settings import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    checks = {
        "postgres": _check_postgres(db),
        "qdrant": _check_http_endpoint(settings.qdrant_url),
        "redis": _check_redis(settings.redis_url),
        "storage": _check_storage(settings.storage_root),
    }
    ready_status = all(check["ok"] for check in checks.values())
    status_code = 200 if ready_status else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if ready_status else "degraded", "checks": checks},
    )


def _check_postgres(db: Session) -> dict[str, object]:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - message depends on driver
        return {"ok": False, "detail": exc.__class__.__name__}
    return {"ok": True}


def _check_http_endpoint(base_url: str) -> dict[str, object]:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"ok": False, "detail": "invalid_url"}
    url = base_url.rstrip("/") + "/readyz"
    try:
        with urlopen(url, timeout=2) as response:
            return {"ok": 200 <= response.status < 500}
    except URLError as exc:
        return {"ok": False, "detail": exc.__class__.__name__}
    except Exception as exc:  # pragma: no cover - defensive dependency check
        return {"ok": False, "detail": exc.__class__.__name__}


def _check_redis(redis_url: str) -> dict[str, object]:
    try:
        client = redis.Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
        client.ping()
    except Exception as exc:  # pragma: no cover - message depends on runtime service
        return {"ok": False, "detail": exc.__class__.__name__}
    return {"ok": True}


def _check_storage(storage_root: Path) -> dict[str, object]:
    try:
        storage_root.mkdir(parents=True, exist_ok=True)
        if not storage_root.is_dir():
            return {"ok": False, "detail": "not_a_directory"}
    except OSError as exc:
        return {"ok": False, "detail": exc.__class__.__name__}
    return {"ok": True}
