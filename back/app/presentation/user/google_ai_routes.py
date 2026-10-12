"""Account connection is separate from sign-in and API-key management."""

import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from app.application.user.google_ai_client import GoogleConnectionError
from app.application.user.google_ai_connection import GOOGLE_AI_COOKIE
from app.application.user.session import parse_access_token_claims
from .auth_routes import SESSION_COOKIE_NAME, frontend_url
from .dependencies import current_user_mail, google_ai_connection, email_verification, user_repo
from .technical_profile_routes import verification_error
from app.application.user.verify_email import EmailVerificationError

router = APIRouter(tags=["GoogleConnection"])


class ProjectSelection(BaseModel):
    projectId: str = Field(min_length=6, max_length=63)


def failure(exc):
    from fastapi import HTTPException
    return HTTPException(exc.status, detail={"message": str(exc), "code": exc.code})


def same_origin(request):
    origin = request.headers.get("origin")
    if origin and origin.rstrip("/") != frontend_url():
        raise failure(GoogleConnectionError("Abrí esta configuración desde BloqIA.", "permission", 403))


@router.get("/technical-profile/google")
def status(mail=Depends(current_user_mail), connection=Depends(google_ai_connection)):
    return connection.status(mail)


@router.post("/technical-profile/google/start")
def start(request: Request, mail=Depends(current_user_mail), connection=Depends(google_ai_connection), verification=Depends(email_verification)):
    same_origin(request)
    try:
        verification.require_verified(mail)
        url, browser = connection.start(mail)
    except GoogleConnectionError as exc:
        raise failure(exc)
    except EmailVerificationError as exc:
        raise verification_error(exc)
    response = JSONResponse({"authorizationUrl": url})
    response.set_cookie(GOOGLE_AI_COOKIE, browser, max_age=600, httponly=True, samesite="lax", secure=os.getenv("ENVIRONMENT") == "production", path="/")
    return response


@router.get("/technical-profile/google/callback")
def callback(request: Request, state: str | None = None, code: str | None = None, error: str | None = None,
             connection=Depends(google_ai_connection), users=Depends(user_repo)):
    claims = parse_access_token_claims(request.cookies.get(SESSION_COOKIE_NAME, ""))
    user = users.get(claims.get("sub")) if claims else None
    mail = user.mail if user is not None and claims.get("ver", 0) == user.auth_version else None
    result = "state"
    if mail:
        try:
            connection.complete(mail, state, request.cookies.get(GOOGLE_AI_COOKIE), code, error)
            result = "connected"
        except GoogleConnectionError as exc:
            result = exc.code
    response = RedirectResponse(f"{frontend_url()}/perfil-tecnico?google={result}#provider-google", status_code=302)
    response.delete_cookie(GOOGLE_AI_COOKIE, path="/")
    return response


@router.get("/technical-profile/google/projects")
def projects(mail=Depends(current_user_mail), connection=Depends(google_ai_connection)):
    try:
        return {"projects": connection.projects(mail)}
    except GoogleConnectionError as exc:
        raise failure(exc)


@router.post("/technical-profile/google/project")
def select_project(payload: ProjectSelection, request: Request, mail=Depends(current_user_mail), connection=Depends(google_ai_connection), verification=Depends(email_verification)):
    same_origin(request)
    try:
        verification.require_verified(mail)
        return connection.select_project(mail, payload.projectId)
    except GoogleConnectionError as exc:
        raise failure(exc)
    except EmailVerificationError as exc:
        raise verification_error(exc)


@router.delete("/technical-profile/google")
def disconnect(request: Request, mail=Depends(current_user_mail), connection=Depends(google_ai_connection)):
    same_origin(request)
    return connection.disconnect(mail)
