CREATE TABLE users (
    mail TEXT PRIMARY KEY,
    password_status BOOLEAN NOT NULL DEFAULT FALSE,
    age INTEGER NOT NULL CHECK (age > 0),
    profession TEXT NOT NULL,
    display_name TEXT,
    login_provider_status TEXT NOT NULL,
    technical_profile_status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE password_credentials (
    user_mail TEXT PRIMARY KEY REFERENCES users(mail) ON DELETE CASCADE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE external_login_links (
    provider TEXT NOT NULL,
    external_subject TEXT NOT NULL,
    user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    provided_mail TEXT NOT NULL,
    provided_display_name TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    last_used_at TIMESTAMPTZ,
    PRIMARY KEY (provider, external_subject),
    UNIQUE (provider, provided_mail)
);

CREATE TABLE ai_providers (
    provider_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    description TEXT
);

CREATE TABLE ai_models (
    model_id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL REFERENCES ai_providers(provider_id) ON DELETE CASCADE,
    display_name TEXT NOT NULL,
    availability_status TEXT NOT NULL,
    capabilities TEXT[] NOT NULL DEFAULT '{}'
);

CREATE TABLE provider_tokens (
    token_id TEXT PRIMARY KEY,
    user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    provider_id TEXT NOT NULL REFERENCES ai_providers(provider_id) ON DELETE CASCADE,
    masked_token_label TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    last_validated_at TIMESTAMPTZ,
    UNIQUE (user_mail, provider_id)
);
