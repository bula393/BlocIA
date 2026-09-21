import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, Request as FastAPIRequest
from fastapi.responses import JSONResponse, RedirectResponse

from app.application.user.complete_google_registration import CompleteGoogleRegistration
from app.application.user.google_auth import GoogleAuth, GoogleCompletionRequired
from app.application.user.login_with_password import InvalidCredentialsError, LoginWithPassword
from app.application.user.register_user import DuplicateMailError, RegisterUser
from app.application.user.session import ACCESS_TOKEN_TTL_SECONDS, parse_access_token
from .auth_schemas import GoogleRegistrationCompletionRequest, LoginRequest, RegisterRequest
from .dependencies import credential_repo, external_link_repo, user_repo
from .errors import error_response, validation_error_response
from .serializers import user_profile

router = APIRouter(tags=["Auth"])

SESSION_COOKIE_NAME = "bloqia_session"


def frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")


def callback_url() -> str:
    return os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")


def result_secret() -> bytes:
    secret = os.getenv("GOOGLE_SESSION_SECRET") or os.getenv("ACCESS_TOKEN_SECRET")
    if secret:
        return secret.encode()
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("GOOGLE_SESSION_SECRET or ACCESS_TOKEN_SECRET must be configured in production")
    return b"development-only-google-session-secret"


def encode_result(result: dict) -> str:
    encoded = base64.urlsafe_b64encode(json.dumps(result, separators=(",", ":")).encode()).decode()
    signature = hmac.new(result_secret(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def decode_result(value: str | None) -> dict | None:
    if not value:
        return None
    try:
        encoded, signature = value.rsplit(".", 1)
        expected = hmac.new(result_secret(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        return json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, binascii.Error):
        return None


def set_session_cookie(response: JSONResponse | RedirectResponse, token: str) -> None:
    """Persist authentication only for the current browser lifetime.

    Omitting both ``max_age`` and ``expires`` deliberately creates a session
    cookie.  JavaScript cannot inspect it, and it is sent only to this site.
    """
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        secure=os.getenv("ENVIRONMENT") == "production",
        path="/",
    )


def authenticated_response(user: object, token: str, status_code: int = 200) -> JSONResponse:
    response = JSONResponse(
        {
            "user": user_profile(user),
            "accessToken": token,
            "expiresInSeconds": ACCESS_TOKEN_TTL_SECONDS,
        },
        status_code=status_code,
    )
    response.headers["Cache-Control"] = "no-store"
    set_session_cookie(response, token)
    return response


def google_identity(code: str) -> dict:
    data = urlencode({
        "code": code,
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": callback_url(),
        "grant_type": "authorization_code",
    }).encode()
    token_request = Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    with urlopen(token_request, timeout=10) as response:  # nosec B310: fixed Google endpoint
        token = json.loads(response.read().decode())
    id_token = token.get("id_token")
    if not id_token:
        raise ValueError("Google did not return an identity token")
    with urlopen(f"https://oauth2.googleapis.com/tokeninfo?{urlencode({'id_token': id_token})}", timeout=10) as response:  # nosec B310: fixed Google endpoint
        identity = json.loads(response.read().decode())
    if identity.get("aud") != os.environ["GOOGLE_CLIENT_ID"] or identity.get("iss") not in ("accounts.google.com", "https://accounts.google.com") or identity.get("email_verified") not in ("true", True):
        raise ValueError("Google identity could not be validated")
    if not identity.get("sub") or not identity.get("email"):
        raise ValueError("Google identity is incomplete")
    return identity


@router.post("/auth/login")
def login(payload: LoginRequest, users=Depends(user_repo), credentials=Depends(credential_repo)):
    try:
        user, token = LoginWithPassword(users, credentials).execute(payload.mail, payload.password)
        return authenticated_response(user, token)
    except InvalidCredentialsError:
        raise error_response("Invalid credentials", 401)


@router.get("/auth/google/start")
def google_start():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id or not os.getenv("GOOGLE_CLIENT_SECRET"):
        return RedirectResponse(f"{frontend_url()}/auth/google/callback?error=configuration", status_code=302)
    state = secrets.token_urlsafe(32)
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": client_id,
        "redirect_uri": callback_url(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    })
    response = RedirectResponse(authorization_url, status_code=302)
    response.set_cookie("bloqia_google_state", state, max_age=600, httponly=True, samesite="lax", secure=os.getenv("ENVIRONMENT") == "production")
    return response


@router.get("/auth/google/callback")
def google_callback(request: FastAPIRequest, code: str | None = None, state: str | None = None, error: str | None = None, users=Depends(user_repo), links=Depends(external_link_repo)):
    state_is_valid = state is not None and secrets.compare_digest(state, request.cookies.get("bloqia_google_state", ""))
    if not state_is_valid:
        response = RedirectResponse(f"{frontend_url()}/auth/google/callback?error=state", status_code=302)
        response.delete_cookie("bloqia_google_state")
        return response
    if error or not code:
        response = RedirectResponse(f"{frontend_url()}/auth/google/callback?error=provider", status_code=302)
        response.delete_cookie("bloqia_google_state")
        return response
    try:
        identity = google_identity(code)
        user, token = GoogleAuth(users, links).complete(identity["sub"], state, identity["email"])
        result = {"user": user_profile(user), "accessToken": token, "expiresInSeconds": ACCESS_TOKEN_TTL_SECONDS}
    except GoogleCompletionRequired as exc:
        result = {"registrationToken": exc.registration_token, "missingFields": exc.missing_fields, "prefilledFields": exc.prefilled_fields}
    except Exception:
        response = RedirectResponse(f"{frontend_url()}/auth/google/callback?error=provider", status_code=302)
        response.delete_cookie("bloqia_google_state")
        return response
    response = RedirectResponse(f"{frontend_url()}/auth/google/callback", status_code=302)
    response.delete_cookie("bloqia_google_state")
    if "accessToken" in result:
        set_session_cookie(response, result["accessToken"])
    response.set_cookie("bloqia_google_result", encode_result(result), max_age=120, httponly=True, samesite="lax", secure=os.getenv("ENVIRONMENT") == "production")
    return response


@router.get("/auth/google/session")
def google_session(request: FastAPIRequest):
    result = decode_result(request.cookies.get("bloqia_google_result"))
    if not result:
        raise error_response("Google session is missing or expired", 401)
    response = JSONResponse(result)
    response.headers["Cache-Control"] = "no-store"
    response.delete_cookie("bloqia_google_result")
    return response


@router.get("/auth/session")
def session(request: FastAPIRequest, users=Depends(user_repo)):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    mail = parse_access_token(token) if token else None
    user = users.get(mail) if mail else None
    if not user:
        raise error_response("Session is missing or expired", 401)
    return authenticated_response(user, token)


@router.post("/auth/logout", status_code=204)
def logout():
    response = JSONResponse(content=None, status_code=204)
    response.headers["Cache-Control"] = "no-store"
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.delete_cookie("bloqia_google_result")
    response.delete_cookie("bloqia_google_state")
    return response


@router.post("/auth/register", status_code=201)
def register(payload: RegisterRequest, users=Depends(user_repo), credentials=Depends(credential_repo)):
    try:
        user, token = RegisterUser(users, credentials).execute(payload.mail, payload.password, payload.age, payload.profession)
        return authenticated_response(user, token, status_code=201)
    except DuplicateMailError:
        raise error_response("Mail already registered", 409)
    except ValueError as exc:
        raise validation_error_response(str(exc), {"password": str(exc)})


@router.post("/auth/register/complete-google", status_code=201)
def complete_google_registration(payload: GoogleRegistrationCompletionRequest, users=Depends(user_repo), links=Depends(external_link_repo)):
    try:
        user, token = CompleteGoogleRegistration(users, links).execute(payload.registrationToken, payload.age, payload.profession)
        return authenticated_response(user, token, status_code=201)
    except DuplicateMailError:
        raise error_response("Mail already registered", 409)
    except ValueError as exc:
        raise validation_error_response(str(exc), {"registration": str(exc)})
