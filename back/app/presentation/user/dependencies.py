from fastapi import Cookie, Depends, Header, HTTPException

from app.application.user.session import parse_access_token
from app.infrastructure.user.postgres_repositories import (
    AIModelRepositoryImpl,
    AIProviderRepositoryImpl,
    ExternalLoginLinkRepositoryImpl,
    PasswordCredentialRepositoryImpl,
    ProviderTokenRepositoryImpl,
    UserRepositoryImpl,
)


def user_repo() -> UserRepositoryImpl:
    return UserRepositoryImpl()


def credential_repo() -> PasswordCredentialRepositoryImpl:
    return PasswordCredentialRepositoryImpl()


def external_link_repo() -> ExternalLoginLinkRepositoryImpl:
    return ExternalLoginLinkRepositoryImpl()


def provider_repo() -> AIProviderRepositoryImpl:
    return AIProviderRepositoryImpl()


def model_repo() -> AIModelRepositoryImpl:
    return AIModelRepositoryImpl()


def token_repo() -> ProviderTokenRepositoryImpl:
    return ProviderTokenRepositoryImpl()


def current_user_mail(
    authorization: str | None = Header(default=None),
    bloqia_session: str | None = Cookie(default=None),
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
        mail = parse_access_token(token)
        if mail:
            return mail
    raise HTTPException(status_code=401, detail={"message": "Authentication required"})
