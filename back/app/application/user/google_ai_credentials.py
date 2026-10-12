"""OAuth credentials cannot be confused with a user's static API key."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GoogleAICredential:
    access_token: str = field(repr=False)
    project_id: str

    def headers(self):
        return {"Authorization": f"Bearer {self.access_token}", "x-goog-user-project": self.project_id}


def google_headers(credential):
    return credential.headers() if isinstance(credential, GoogleAICredential) else {"x-goog-api-key": credential}
