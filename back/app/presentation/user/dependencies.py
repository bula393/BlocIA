import os

from fastapi import Cookie, Depends, Header, HTTPException

from app.application.user.session import parse_access_token_claims
from app.infrastructure.database import get_database
from app.infrastructure.abuse_limits import AbuseLimitRepository
from app.application.user.verify_email import VerifyEmail
from app.infrastructure.user.email_verification_repository import EmailVerificationRepository
from app.infrastructure.user.smtp_email_sender import SmtpEmailSender
from app.infrastructure.user.sqlite_repositories import (
    ModelRepository,
    ProviderRepository,
    ExternalLinkRepository,
    CredentialRepository,
    TokenRepository,
    UsageRepository,
    UserRepository,
)


def user_repo(database=Depends(get_database)):
    return UserRepository(database)


def credential_repo(database=Depends(get_database)):
    return CredentialRepository(database)


def external_link_repo(database=Depends(get_database)):
    return ExternalLinkRepository(database)


def provider_repo(database=Depends(get_database)):
    return ProviderRepository(database)


def model_repo(database=Depends(get_database)):
    return ModelRepository(database)


def token_repo(database=Depends(get_database)):
    return TokenRepository(database)


def usage_repo(database=Depends(get_database)):
    return UsageRepository(database)


def abuse_limits(database=Depends(get_database)):
    return AbuseLimitRepository(database)


def email_verification(database=Depends(get_database), limits=Depends(abuse_limits)):
    return VerifyEmail(EmailVerificationRepository(database), SmtpEmailSender(),
                       os.getenv("ACCESS_TOKEN_SECRET", ""), abuse_limits=limits)


def google_ai_connection(database=Depends(get_database)):
    from app.application.user.google_ai_connection import GoogleAIConnection
    from app.infrastructure.user.provider_oauth_repository import ProviderOAuthRepository
    return GoogleAIConnection(ProviderOAuthRepository(database))


def current_user_mail(
    authorization: str | None = Header(default=None),
    bloqia_session: str | None = Cookie(default=None),
    users=Depends(user_repo),
) -> str:
    """Accept the in-memory API token or the browser-session cookie.

    The latter lets a refreshed page keep working even before the frontend has
    restored its short-lived in-memory copy of the access token.
    """
    candidates: list[str] = []
    if authorization and authorization.lower().startswith("bearer "):
        candidates.append(authorization.split(" ", 1)[1])
    if bloqia_session:
        candidates.append(bloqia_session)

    for token in candidates:
        claims = parse_access_token_claims(token)
        if claims:
            user = users.get(claims.get("sub"))
            if user is not None and claims.get("ver", 0) == user.auth_version:
                return user.mail
    raise HTTPException(status_code=401, detail={"message": "Authentication required"})
