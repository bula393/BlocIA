import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import time
from functools import partial
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
GOOGLE_TRANSACTION_TTL_SECONDS = 600
GOOGLE_RESULT_TTL_SECONDS = 120


def frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://localhost:5173").strip().rstrip("/")


def callback_url() -> str:
    configured = os.getenv("GOOGLE_REDIRECT_URI", "").strip()
    if configured:
        return configured
    if os.getenv("ENVIRONMENT", "development").strip().lower() == "production":
        return f"{frontend_url()}/api/auth/google/callback"
    return "http://localhost:8000/auth/google/callback"


def result_secret() -> bytes:
    secret = os.getenv("GOOGLE_SESSION_SECRET") or os.getenv("ACCESS_TOKEN_SECRET")
    if secret:
        return secret.encode()
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("GOOGLE_SESSION_SECRET or ACCESS_TOKEN_SECRET must be configured in production")
    return b"development-only-google-session-secret"


def encode_google_payload(payload: dict, purpose: str, ttl_seconds: int) -> str:
    envelope = {"purpose": purpose, "exp": int(time.time()) + ttl_seconds, "payload": payload}
    encoded = base64.urlsafe_b64encode(json.dumps(envelope, separators=(",", ":")).encode()).decode()
    signature = hmac.new(result_secret(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def decode_google_payload(value: str | None, purpose: str) -> dict | None:
    if not value or len(value) > 16384:
        return None
    try:
        encoded, signature = value.rsplit(".", 1)
        expected = hmac.new(result_secret(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        envelope = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
        if not isinstance(envelope, dict) or envelope.get("purpose") != purpose:
            return None
        expires_at = envelope.get("exp")
        if type(expires_at) is not int or expires_at <= int(time.time()):
            return None
        payload = envelope.get("payload")
        return payload if isinstance(payload, dict) else None
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, binascii.Error):
        return None


def encode_result(result: dict) -> str:
    return encode_google_payload(result, "google-result", GOOGLE_RESULT_TTL_SECONDS)


def decode_result(value: str | None) -> dict | None:
    return decode_google_payload(value, "google-result")


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


def verify_google_id_token(id_token: str, client_id: str) -> dict:
    # The official verifier checks Google's public-key signature, audience,
    # issuer, issued-at time and expiration; tokeninfo is a debugging endpoint.
    from google.auth.transport.requests import Request as GoogleAuthRequest
    from google.oauth2.id_token import verify_oauth2_token

    identity = verify_oauth2_token(id_token, partial(GoogleAuthRequest(), timeout=10), client_id)
    if type(identity.get("exp")) is not int or identity["exp"] <= int(time.time()):
        raise ValueError("Google identity token is expired")
    return identity


def google_identity(code: str, nonce: str) -> dict:
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
    identity = verify_google_id_token(id_token, os.environ["GOOGLE_CLIENT_ID"])
    if identity.get("email_verified") not in ("true", True):
        raise ValueError("Google identity could not be validated")
    if not isinstance(identity.get("sub"), str) or not identity["sub"] or not isinstance(identity.get("email"), str) or not identity["email"]:
        raise ValueError("Google identity is incomplete")
    returned_nonce = identity.get("nonce")
    if not nonce or not isinstance(returned_nonce, str) or not secrets.compare_digest(nonce.encode(), returned_nonce.encode()):
        raise ValueError("Google identity nonce could not be validated")
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
    nonce = secrets.token_urlsafe(32)
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": client_id,
        "redirect_uri": callback_url(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "nonce": nonce,
        "prompt": "select_account",
    })
    response = RedirectResponse(authorization_url, status_code=302)
    transaction = encode_google_payload({"state": state, "nonce": nonce}, "google-transaction", GOOGLE_TRANSACTION_TTL_SECONDS)
    response.set_cookie("bloqia_google_state", transaction, max_age=GOOGLE_TRANSACTION_TTL_SECONDS, httponly=True, samesite="lax", secure=os.getenv("ENVIRONMENT") == "production", path="/")
    response.delete_cookie("bloqia_google_result", path="/")
    return response


@router.get("/auth/google/callback")
def google_callback(request: FastAPIRequest, code: str | None = None, state: str | None = None, error: str | None = None, users=Depends(user_repo), links=Depends(external_link_repo)):
    transaction = decode_google_payload(request.cookies.get("bloqia_google_state"), "google-transaction")
    expected_state = transaction.get("state") if transaction else None
    nonce = transaction.get("nonce") if transaction else None
    state_is_valid = bool(state and isinstance(expected_state, str) and isinstance(nonce, str)
                          and nonce and secrets.compare_digest(state.encode(), expected_state.encode()))
    if not state_is_valid:
        response = RedirectResponse(f"{frontend_url()}/auth/google/callback?error=state", status_code=302)
        response.delete_cookie("bloqia_google_state")
        response.delete_cookie("bloqia_google_result")
        return response
    if error or not code:
        response = RedirectResponse(f"{frontend_url()}/auth/google/callback?error=provider", status_code=302)
        response.delete_cookie("bloqia_google_state")
        response.delete_cookie("bloqia_google_result")
        return response
    try:
        identity = google_identity(code, nonce)
        user, token = GoogleAuth(users, links).complete(identity["sub"], state, identity["email"])
        result = {"user": user_profile(user), "accessToken": token, "expiresInSeconds": ACCESS_TOKEN_TTL_SECONDS}
    except GoogleCompletionRequired as exc:
        result = {"registrationToken": exc.registration_token, "missingFields": exc.missing_fields, "prefilledFields": exc.prefilled_fields}
    except Exception:
        response = RedirectResponse(f"{frontend_url()}/auth/google/callback?error=provider", status_code=302)
        response.delete_cookie("bloqia_google_state")
        response.delete_cookie("bloqia_google_result")
        return response
    response = RedirectResponse(f"{frontend_url()}/auth/google/callback", status_code=302)
    response.delete_cookie("bloqia_google_state")
    if "accessToken" in result:
        set_session_cookie(response, result["accessToken"])
    response.set_cookie("bloqia_google_result", encode_result(result), max_age=GOOGLE_RESULT_TTL_SECONDS, httponly=True, samesite="lax", secure=os.getenv("ENVIRONMENT") == "production", path="/")
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
