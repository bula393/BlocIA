from datetime import datetime, timezone
import hashlib
import json
import sqlite3
import time
from uuid import uuid4


class ConversationNotFoundError(Exception):
    pass


class TurnConflictError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def conversation(row):
    return {"id": row["id"], "title": row["title"], "createdAt": row["created_at"], "updatedAt": row["updated_at"]}


class ChatRepository:
    def __init__(self, database):
        self.database = database

    def create(self, mail):
        identifier, timestamp = str(uuid4()), now()
        self.database.execute("INSERT INTO conversations(id,user_mail,title,created_at,updated_at) VALUES (?,?,?,?,?)", (identifier, mail, "Nuevo chat", timestamp, timestamp))
        return self.get(mail, identifier)

    def list(self, mail):
        return [conversation(row) for row in self.database.query("SELECT * FROM conversations WHERE user_mail=? ORDER BY updated_at DESC LIMIT 100", (mail,))]

    def get(self, mail, identifier):
        rows = self.database.query("SELECT * FROM conversations WHERE user_mail=? AND id=?", (mail, identifier))
        if not rows:
            raise ConversationNotFoundError("No se encontró esta conversación.")
        return conversation(rows[0])

    def messages(self, mail, identifier):
        self.get(mail, identifier)
        rows = self.database.query("SELECT * FROM (SELECT * FROM messages WHERE conversation_id=? ORDER BY sequence DESC LIMIT 200) ORDER BY sequence", (identifier,))
        return [{"id": row["id"], "role": row["role"], "content": row["content"], "createdAt": row["created_at"], "requestId": row["request_id"], "classification": json.loads(row["classification"]) if row["classification"] else None} for row in rows]

    def delete(self, mail, identifier):
        with self.database.transaction():
            self.get(mail, identifier)
            self.database.execute("DELETE FROM conversations WHERE id=? AND user_mail=?", (identifier, mail))

    def reserve(self, mail, identifier, request_id, prompt):
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        with self.database.transaction():
            self.get(mail, identifier)
            self.database.execute("UPDATE chat_turns SET state='failed' WHERE conversation_id=? AND state='pending' AND started_at<?", (identifier, time.time() - 300))
            previous = self.database.query("SELECT * FROM chat_turns WHERE conversation_id=? AND request_id=?", (identifier, request_id))
            if previous:
                if previous[0]["prompt_hash"] != prompt_hash:
                    raise TurnConflictError("Este envío ya pertenece a otra consulta.")
                if previous[0]["state"] == "completed":
                    return False
                if previous[0]["state"] == "pending":
                    raise TurnConflictError("La consulta sigue en proceso. Esperá antes de reintentar.")
            try:
                self.database.execute("INSERT INTO chat_turns(conversation_id,request_id,prompt_hash,state,started_at) VALUES (?,?,?,'pending',?) ON CONFLICT(conversation_id,request_id) DO UPDATE SET state='pending',started_at=excluded.started_at", (identifier, request_id, prompt_hash, time.time()))
            except sqlite3.IntegrityError as error:
                raise TurnConflictError("Ya hay una respuesta en curso para esta conversación.") from error
        return True

    def complete(self, mail, identifier, request_id, prompt, answer, classification):
        with self.database.transaction():
            self.get(mail, identifier)
            timestamp = now()
            for role, content in [("user", prompt), ("assistant", answer)]:
                self.database.execute("INSERT INTO messages(id,conversation_id,request_id,role,content,created_at,classification) VALUES (?,?,?,?,?,?,?)", (str(uuid4()), identifier, request_id, role, content, timestamp, json.dumps(classification)))
            self.database.execute("UPDATE chat_turns SET state='completed' WHERE conversation_id=? AND request_id=?", (identifier, request_id))
            self.database.execute("UPDATE conversations SET title=CASE WHEN title='Nuevo chat' THEN ? ELSE title END,updated_at=? WHERE id=?", (prompt[:70], timestamp, identifier))

    def fail(self, identifier, request_id):
        self.database.execute("UPDATE chat_turns SET state='failed' WHERE conversation_id=? AND request_id=? AND state='pending'", (identifier, request_id))
