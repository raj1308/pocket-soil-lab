from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}


@router.get("/api/version")
def version() -> dict[str, str]:
    return {"version": settings.app_version}
