"""Public operational probes; never expose provider keys or private model status."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.application.chat.local_models import local_models
from app.infrastructure.database import get_database
from app.infrastructure.runtime_settings import RuntimeSettings


router = APIRouter(tags=["Health"])


@router.get("/health")
def health(database=Depends(get_database)):
    result = database.health()
    return JSONResponse({"database": result, "release": RuntimeSettings.from_environment().release},
                        status_code=200 if result["ok"] else 503)


@router.get("/ready")
def ready(database=Depends(get_database), models=Depends(local_models)):
    database_ready = bool(database.health()["ok"])
    inference_release = None
    try:
        model_status = models.status()
        classifier_ready = bool(model_status.get("classifierReady", False))
        inference_release = model_status.get("release")
    except Exception:
        classifier_ready = False
    available = database_ready and classifier_ready
    details = {"ready": available, "databaseReady": database_ready,
               "classifierReady": classifier_ready, "release": RuntimeSettings.from_environment().release}
    if inference_release is not None:
        details["inferenceRelease"] = inference_release
    return JSONResponse(details,
                        status_code=200 if available else 503)
