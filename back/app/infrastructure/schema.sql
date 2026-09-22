BEGIN IMMEDIATE;
CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS users (
    mail TEXT PRIMARY KEY,
    payload TEXT NOT NULL CHECK(json_valid(payload))
      CHECK(json_extract(payload, '$.age') > 0)
      CHECK(length(trim(json_extract(payload, '$.profession'))) > 0)
      CHECK(json_extract(payload, '$.mail') = mail)
);
CREATE TABLE IF NOT EXISTS credentials (
    user_mail TEXT PRIMARY KEY REFERENCES users(mail) ON DELETE CASCADE,
    payload TEXT NOT NULL CHECK(json_valid(payload))
);
CREATE TABLE IF NOT EXISTS external_links (
    provider TEXT NOT NULL, external_subject TEXT NOT NULL,
    user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    payload TEXT NOT NULL CHECK(json_valid(payload)), PRIMARY KEY(provider, external_subject)
);
CREATE TABLE IF NOT EXISTS providers (provider_id TEXT PRIMARY KEY, payload TEXT NOT NULL CHECK(json_valid(payload)));
CREATE TABLE IF NOT EXISTS models (
    provider_id TEXT NOT NULL REFERENCES providers(provider_id) ON DELETE CASCADE,
    model_id TEXT NOT NULL, payload TEXT NOT NULL CHECK(json_valid(payload)), PRIMARY KEY(provider_id, model_id)
);
CREATE TABLE IF NOT EXISTS provider_tokens (
    user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    provider_id TEXT NOT NULL REFERENCES providers(provider_id) ON DELETE CASCADE,
    payload TEXT NOT NULL CHECK(json_valid(payload)), PRIMARY KEY(user_mail, provider_id)
);
CREATE TABLE IF NOT EXISTS token_secrets (
    user_mail TEXT NOT NULL, provider_id TEXT NOT NULL, ciphertext BLOB NOT NULL,
    PRIMARY KEY(user_mail, provider_id),
    FOREIGN KEY(user_mail, provider_id) REFERENCES provider_tokens(user_mail, provider_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS usage_events (
    id INTEGER PRIMARY KEY, user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    payload TEXT NOT NULL CHECK(json_valid(payload))
);
CREATE INDEX IF NOT EXISTS usage_by_user ON usage_events(user_mail);
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY, user_mail TEXT NOT NULL REFERENCES users(mail) ON DELETE CASCADE,
    title TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS conversations_by_user ON conversations(user_mail, updated_at DESC);
CREATE TABLE IF NOT EXISTS chat_turns (
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    request_id TEXT NOT NULL, prompt_hash TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('pending', 'completed', 'failed')),
    started_at REAL NOT NULL, PRIMARY KEY(conversation_id, request_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS one_pending_turn ON chat_turns(conversation_id) WHERE state = 'pending';
CREATE TABLE IF NOT EXISTS messages (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL UNIQUE,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    request_id TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK(length(content) > 0), created_at TEXT NOT NULL,
    classification TEXT CHECK(classification IS NULL OR json_valid(classification)),
    UNIQUE(conversation_id, request_id, role),
    FOREIGN KEY(conversation_id, request_id) REFERENCES chat_turns(conversation_id, request_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS messages_by_conversation ON messages(conversation_id, sequence);
PRAGMA user_version = 1;
COMMIT;
