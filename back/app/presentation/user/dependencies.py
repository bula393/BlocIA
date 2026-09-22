from fastapi import Cookie, Depends, Header, HTTPException

from app.application.user.session import parse_access_token
from app.infrastructure.database import get_database
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
