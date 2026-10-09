from datetime import datetime, timezone
import hashlib
import json
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
        return [{"id": row["id"], "role": row["role"], "content": row["content"], "createdAt": row["created_at"], "requestId": row["request_id"], "classification": json.loads(row["classification"]) if row["classification"] else None, "providerId": row["provider_id"], "modelId": row["model_id"]} for row in rows]

    def recent_context(self, mail, identifier):
        """Fetch the last four answered turns without decoding the full history."""
        self.get(mail, identifier)
        rows = self.database.query(
            "SELECT question.content AS question, answer.content AS answer, answer.request_id, answer.provider_id "
            "FROM messages AS answer JOIN messages AS question "
            "ON question.conversation_id=answer.conversation_id AND question.request_id=answer.request_id AND question.role='user' "
            "WHERE answer.conversation_id=? AND answer.role='assistant' AND answer.provider_id IS NOT NULL "
            "ORDER BY answer.sequence DESC LIMIT 4", (identifier,),
        )
        messages = []
        for row in reversed(rows):
            messages.extend([
                {"role": "user", "content": row["question"], "requestId": row["request_id"]},
                {"role": "assistant", "content": row["answer"], "requestId": row["request_id"], "providerId": row["provider_id"]},
            ])
        return messages

    def delete(self, mail, identifier):
        with self.database.transaction():
            self.get(mail, identifier)
            self.database.execute("DELETE FROM conversations WHERE id=? AND user_mail=?", (identifier, mail))

    def is_completed(self, mail, identifier, request_id, prompt):
        self.get(mail, identifier)
        rows = self.database.query(
            "SELECT prompt_hash,state FROM chat_turns WHERE conversation_id=? AND request_id=?",
            (identifier, request_id),
        )
        if not rows:
            return False
        if rows[0]["prompt_hash"] != hashlib.sha256(prompt.encode()).hexdigest():
            raise TurnConflictError("Este envío ya pertenece a otra consulta.")
        return rows[0]["state"] == "completed"

    def reserve(self, mail, identifier, request_id, prompt):
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        with self.database.transaction():
            self.get(mail, identifier)
            self.database.execute(
                "UPDATE chat_turns SET state='failed' WHERE state='pending' AND started_at<? "
                "AND conversation_id IN (SELECT id FROM conversations WHERE user_mail=?)",
                (time.time() - 300, mail),
            )
            previous = self.database.query("SELECT * FROM chat_turns WHERE conversation_id=? AND request_id=?", (identifier, request_id))
            if previous:
                if previous[0]["prompt_hash"] != prompt_hash:
                    raise TurnConflictError("Este envío ya pertenece a otra consulta.")
                if previous[0]["state"] == "completed":
                    return False
                if previous[0]["state"] == "pending":
                    raise TurnConflictError("La consulta sigue en proceso. Esperá antes de reintentar.")
            pending = self.database.query(
                "SELECT 1 FROM chat_turns JOIN conversations ON conversations.id=chat_turns.conversation_id "
                "WHERE conversations.user_mail=? AND chat_turns.state='pending' LIMIT 1",
                (mail,),
            )
            if pending:
                raise TurnConflictError("Ya hay una respuesta en curso. Esperá antes de enviar otra consulta.")
            try:
                self.database.execute("INSERT INTO chat_turns(conversation_id,request_id,prompt_hash,state,started_at) VALUES (?,?,?,'pending',?) ON CONFLICT(conversation_id,request_id) DO UPDATE SET state='pending',started_at=excluded.started_at,phase='classifying'", (identifier, request_id, prompt_hash, time.time()))
            except Exception as error:
                if not self.database.is_integrity_error(error):
                    raise
                raise TurnConflictError("Ya hay una respuesta en curso para esta conversación.") from error
        return True

    def mark_generating(self, identifier, request_id):
        self.database.execute("UPDATE chat_turns SET phase='generating' WHERE conversation_id=? AND request_id=? AND state='pending'", (identifier, request_id))

    def progress(self, mail, identifier, request_id):
        rows = self.database.query(
            "SELECT turns.phase,turns.state FROM chat_turns AS turns "
            "JOIN conversations ON conversations.id=turns.conversation_id "
            "WHERE turns.conversation_id=? AND turns.request_id=? AND conversations.user_mail=?",
            (identifier, request_id, mail),
        )
        if not rows:
            return None
        return {"phase": rows[0]["phase"], "state": rows[0]["state"]}

    def complete(self, mail, identifier, request_id, prompt, answer, classification, provider_id=None, model_id=None):
        with self.database.transaction():
            self.get(mail, identifier)
            timestamp = now()
            messages = [("user", prompt, None, None), ("assistant", answer, provider_id, model_id)]
            for role, content, message_provider, message_model in messages:
                self.database.execute("INSERT INTO messages(id,conversation_id,request_id,role,content,created_at,classification,provider_id,model_id) VALUES (?,?,?,?,?,?,?,?,?)", (str(uuid4()), identifier, request_id, role, content, timestamp, json.dumps(classification), message_provider, message_model))
            completed_at = time.time()
            elapsed = "GREATEST(0,?-started_at)" if self.database.is_postgres else "MAX(0,?-started_at)"
            self.database.execute(f"UPDATE chat_turns SET state='completed',completed_at=?,duration_seconds={elapsed} WHERE conversation_id=? AND request_id=?", (completed_at, completed_at, identifier, request_id))
            self.database.execute("UPDATE conversations SET title=CASE WHEN title='Nuevo chat' THEN ? ELSE title END,updated_at=? WHERE id=?", (prompt[:70], timestamp, identifier))

    def fail(self, identifier, request_id):
        self.database.execute("UPDATE chat_turns SET state='failed' WHERE conversation_id=? AND request_id=? AND state='pending'", (identifier, request_id))
