CREATE TABLE IF NOT EXISTS app_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    mail TEXT PRIMARY KEY,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS credentials (
    user_mail TEXT PRIMARY KEY REFERENCES users(mail) ON DELETE CASCADE,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS email_verifications (
    user_mail TEXT PRIMARY KEY REFERENCES users(mail) ON DELETE CASCADE,
    verified_at DOUBLE PRECISION,
    code_digest TEXT,
    nonce TEXT,
    expires_at DOUBLE PRECISION NOT NULL DEFAULT 0,
    attempts_left INTEGER NOT NULL DEFAULT 0,
    sent_at DOUBLE PRECISION NOT NULL DEFAULT 0,
    window_started_at DOUBLE PRECISION NOT NULL DEFAULT 0,
    send_count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS external_links (
    provider TEXT NOT NULL,
    external_subject TEXT NOT NULL,
    user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    payload TEXT NOT NULL,
    PRIMARY KEY(provider, external_subject)
);
CREATE TABLE IF NOT EXISTS providers (
    provider_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS models (
    provider_id TEXT NOT NULL REFERENCES providers(provider_id) ON DELETE CASCADE,
    model_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    PRIMARY KEY(provider_id, model_id)
);
CREATE TABLE IF NOT EXISTS provider_tokens (
    user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    provider_id TEXT NOT NULL REFERENCES providers(provider_id) ON DELETE CASCADE,
    payload TEXT NOT NULL,
    PRIMARY KEY(user_mail, provider_id)
);
CREATE TABLE IF NOT EXISTS token_secrets (
    user_mail TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    ciphertext BYTEA NOT NULL,
    PRIMARY KEY(user_mail, provider_id),
    FOREIGN KEY(user_mail, provider_id) REFERENCES provider_tokens(user_mail, provider_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS usage_events (
    id BIGSERIAL PRIMARY KEY,
    user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS usage_by_user ON usage_events(user_mail);
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS conversations_by_user ON conversations(user_mail, updated_at DESC);
CREATE TABLE IF NOT EXISTS chat_turns (
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    request_id TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('pending', 'completed', 'failed')),
    started_at DOUBLE PRECISION NOT NULL,
    completed_at DOUBLE PRECISION,
    duration_seconds DOUBLE PRECISION NOT NULL DEFAULT 0,
    phase TEXT NOT NULL DEFAULT 'classifying' CHECK(phase IN ('classifying', 'generating')),
    PRIMARY KEY(conversation_id, request_id)
);
CREATE INDEX IF NOT EXISTS turns_completed_at ON chat_turns(completed_at);
CREATE UNIQUE INDEX IF NOT EXISTS one_pending_turn ON chat_turns(conversation_id) WHERE state = 'pending';
CREATE TABLE IF NOT EXISTS user_usage_locks (
    user_mail TEXT PRIMARY KEY REFERENCES users(mail) ON DELETE CASCADE,
    lock_until DOUBLE PRECISION NOT NULL,
    reasons TEXT NOT NULL,
    updated_at DOUBLE PRECISION NOT NULL
);
CREATE TABLE IF NOT EXISTS user_usage_resets (
    id BIGSERIAL PRIMARY KEY,
    user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    reset_at DOUBLE PRECISION NOT NULL,
    reason TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS usage_resets_by_user ON user_usage_resets(user_mail, reset_at);
CREATE TABLE IF NOT EXISTS messages (
    sequence BIGSERIAL PRIMARY KEY,
    id TEXT NOT NULL UNIQUE,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    request_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK(length(content) > 0),
    created_at TEXT NOT NULL,
    classification TEXT,
    provider_id TEXT,
    model_id TEXT,
    UNIQUE(conversation_id, request_id, role),
    FOREIGN KEY(conversation_id, request_id) REFERENCES chat_turns(conversation_id, request_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS messages_by_conversation ON messages(conversation_id, sequence);
