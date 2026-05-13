from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.api.deps import DbSessionDep, SettingsDep
from app.schemas.common import HealthCheck
from app.services.ollama_service import OllamaService

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health(db: DbSessionDep, settings: SettingsDep) -> HealthCheck:
    """Return application, database, and vector-store health."""
    return await build_health_check(db=db, settings=settings)


@router.get("/health/ready", response_model=HealthCheck)
async def readiness(db: DbSessionDep, settings: SettingsDep) -> HealthCheck:
    """Readiness probe that requires database and Ollama model availability."""
    health_check = await build_health_check(db=db, settings=settings)
    if health_check.status != "ok":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_check.model_dump(),
        )
    return health_check


async def build_health_check(db: DbSessionDep, settings: SettingsDep) -> HealthCheck:
    await db.execute(text("SELECT 1"))
    ollama_health = await OllamaService(settings).health()
    return HealthCheck(
        status="ok" if ollama_health.ready else "degraded",
        environment=settings.app_env,
        database="ok",
        vector_store="configured",
        ollama=ollama_health.status,
        ollama_detail=ollama_health.detail,
    )
