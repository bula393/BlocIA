"""Usage limits and query activity backed by persisted chat turns."""
from datetime import datetime, timezone
import json
import os
import time


USAGE_WINDOW_SECONDS = 24 * 60 * 60
USAGE_LIMIT_SECONDS = 3 * 60 * 60
PERSONAL_QUESTION_LIMIT = 3
DEFAULT_LOCK_DURATION_MINUTES = 24 * 60
LIMIT_REASONS = {
    "usage_time": "Alcanzaste el límite de 3 horas de uso de IA.",
    "personal_questions": "Alcanzaste el límite de 3 consultas personales durante las últimas 24 horas.",
}
REASON_ORDER = {"usage_time": 0, "personal_questions": 1}


def _iso(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat() if epoch is not None else None


def lock_duration_minutes():
    """Use a positive number of minutes, preserving the default for invalid settings."""
    try:
        minutes = int(os.getenv("BLOCIA_LOCK_MINUTES", str(DEFAULT_LOCK_DURATION_MINUTES)))
    except ValueError:
        return DEFAULT_LOCK_DURATION_MINUTES
    return minutes if minutes > 0 else DEFAULT_LOCK_DURATION_MINUTES


class UsageAnalyticsRepository:
    def __init__(self, database):
        self.database = database

    def _label(self, column):
        if self.database.is_postgres:
            return f"({column}::jsonb ->> 'label')"
        return f"json_extract({column},'$.label')"

    def _period_totals(self, mail, now):
        label = self._label("messages.classification")
        reset_rows = self.database.query(
            "SELECT MAX(reset_at) AS reset_at FROM user_usage_resets WHERE user_mail=? AND reset_at<=?",
            (mail, now),
        )
        last_reset = reset_rows[0]["reset_at"] if reset_rows else None
        cutoff = max(now - USAGE_WINDOW_SECONDS, float(last_reset) if last_reset is not None else 0)
        rows = self.database.query(
            "SELECT COALESCE(SUM(turns.duration_seconds),0) AS seconds "
            "FROM chat_turns AS turns JOIN conversations ON conversations.id=turns.conversation_id "
            "WHERE conversations.user_mail=? AND turns.state='completed' AND turns.completed_at>?",
            (mail, cutoff),
        )
        personal = self.database.query(
            "SELECT COUNT(*) AS questions FROM messages "
            "JOIN conversations ON conversations.id=messages.conversation_id "
            "JOIN chat_turns AS turns ON turns.conversation_id=messages.conversation_id AND turns.request_id=messages.request_id "
            "WHERE conversations.user_mail=? AND messages.role='user' AND turns.state='completed' "
            f"AND turns.completed_at>? AND {label} IN ('personal_informativa','personal_decision')",
            (mail, cutoff),
        )
        return round(float(rows[0]["seconds"] or 0)), int(personal[0]["questions"] or 0)

    @staticmethod
    def _threshold_reasons(usage_seconds, personal_questions):
        reasons = []
        if usage_seconds >= USAGE_LIMIT_SECONDS:
            reasons.append("usage_time")
        if personal_questions >= PERSONAL_QUESTION_LIMIT:
            reasons.append("personal_questions")
        return reasons

    def current_lock(self, mail, now=None):
        now = time.time() if now is None else now
        duration_minutes = lock_duration_minutes()
        with self.database.transaction():
            rows = self.database.query("SELECT lock_until,reasons,updated_at FROM user_usage_locks WHERE user_mail=?", (mail,))
            active = bool(rows and float(rows[0]["lock_until"]) > now)
            if active:
                duration_minutes = max(1, round((float(rows[0]["lock_until"]) - float(rows[0]["updated_at"])) / 60))
            if rows and not active:
                # Keep activity intact while starting a fresh allowance when a lock ends.
                # The recorded expiry also survives the next lock replacing this row.
                expired_at = float(rows[0]["lock_until"])
                self.database.execute(
                    "INSERT INTO user_usage_resets(user_mail,reset_at,reason) "
                    "SELECT ?,?,'lock_expired' WHERE NOT EXISTS "
                    "(SELECT 1 FROM user_usage_resets WHERE user_mail=? AND reset_at=?)",
                    (mail, expired_at, mail, expired_at),
                )
            usage_seconds, personal_questions = self._period_totals(mail, now)
            threshold_reasons = self._threshold_reasons(usage_seconds, personal_questions)
            reasons = json.loads(rows[0]["reasons"]) if active else threshold_reasons
            if active:
                combined = sorted(set(reasons) | set(threshold_reasons), key=lambda reason: REASON_ORDER.get(reason, 99))
                if combined != reasons:
                    self.database.execute("UPDATE user_usage_locks SET reasons=? WHERE user_mail=?", (json.dumps(combined), mail))
                reasons = combined
            elif reasons:
                self.database.execute(
                    "INSERT INTO user_usage_locks(user_mail,lock_until,reasons,updated_at) VALUES (?,?,?,?) "
                    "ON CONFLICT(user_mail) DO UPDATE SET lock_until=excluded.lock_until,reasons=excluded.reasons,updated_at=excluded.updated_at",
                    (mail, now + duration_minutes * 60, json.dumps(reasons), now),
                )
                rows = self.database.query("SELECT lock_until,reasons FROM user_usage_locks WHERE user_mail=?", (mail,))
                active = True
        return {
            "blocked": active,
            "reasonCodes": reasons,
            "lockUntil": _iso(float(rows[0]["lock_until"])) if active else None,
            "lockDurationMinutes": duration_minutes,
            "usageSeconds": usage_seconds,
            "usageLimitSeconds": USAGE_LIMIT_SECONDS,
            "personalQuestions": personal_questions,
            "personalQuestionLimit": PERSONAL_QUESTION_LIMIT,
            "personalQuestionsRemaining": max(0, PERSONAL_QUESTION_LIMIT - personal_questions),
        }

    def apply_limits(self, mail, now=None):
        """Persist the configured lock after a completed turn crosses either limit."""
        return self.current_lock(mail, now)

    def dashboard(self, mail, limit=40, offset=0, now=None):
        now = time.time() if now is None else now
        lock = self.current_lock(mail, now)
        message_label = self._label("messages.classification")
        question_label = self._label("question.classification")
        day_expression = ("TO_CHAR(TO_TIMESTAMP(turns.completed_at) AT TIME ZONE 'UTC', 'YYYY-MM-DD')"
                          if self.database.is_postgres else "strftime('%Y-%m-%d',turns.completed_at,'unixepoch')")
        totals = self.database.query(
            "SELECT COUNT(*) AS total, "
            f"SUM(CASE WHEN {message_label} LIKE 'personal_%' THEN 1 ELSE 0 END) AS personal, "
            f"SUM(CASE WHEN {message_label} IS NOT NULL THEN 1 ELSE 0 END) AS classified "
            "FROM messages JOIN conversations ON conversations.id=messages.conversation_id "
            "JOIN chat_turns AS turns ON turns.conversation_id=messages.conversation_id AND turns.request_id=messages.request_id "
            "WHERE conversations.user_mail=? AND messages.role='user' AND turns.state='completed'",
            (mail,),
        )[0]
        by_category_rows = self.database.query(
            f"SELECT COALESCE({message_label},'unclassified') AS label, COUNT(*) AS count "
            "FROM messages JOIN conversations ON conversations.id=messages.conversation_id "
            "JOIN chat_turns AS turns ON turns.conversation_id=messages.conversation_id AND turns.request_id=messages.request_id "
            "WHERE conversations.user_mail=? AND messages.role='user' AND turns.state='completed' GROUP BY label",
            (mail,),
        )
        category_counts = {row["label"]: int(row["count"]) for row in by_category_rows}
        by_provider = self.database.query(
            "SELECT COALESCE(answer.provider_id,'none') AS provider_id, COUNT(*) AS count "
            "FROM messages AS question JOIN conversations ON conversations.id=question.conversation_id "
            "JOIN chat_turns AS turns ON turns.conversation_id=question.conversation_id AND turns.request_id=question.request_id "
            "LEFT JOIN messages AS answer ON answer.conversation_id=question.conversation_id AND answer.request_id=question.request_id AND answer.role='assistant' "
            "WHERE conversations.user_mail=? AND question.role='user' AND turns.state='completed' GROUP BY answer.provider_id ORDER BY COUNT(*) DESC",
            (mail,),
        )
        today = datetime.fromtimestamp(now, timezone.utc).date()
        week_start = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc).timestamp() - 6 * 86400
        daily = self.database.query(
            f"SELECT {day_expression} AS day, COUNT(*) AS count, "
            f"SUM(CASE WHEN {question_label} LIKE 'personal_%' THEN 1 ELSE 0 END) AS personal "
            "FROM chat_turns AS turns JOIN conversations ON conversations.id=turns.conversation_id "
            "JOIN messages AS question ON question.conversation_id=turns.conversation_id AND question.request_id=turns.request_id AND question.role='user' "
            "WHERE conversations.user_mail=? AND turns.state='completed' AND turns.completed_at>=? "
            "GROUP BY day ORDER BY day",
            (mail, week_start),
        )
        total = int(totals["total"] or 0)
        items = self.database.query(
            "SELECT question.content AS prompt, question.created_at, question.classification, answer.provider_id, answer.model_id, "
            "turns.duration_seconds, conversations.id AS conversation_id, conversations.title "
            "FROM messages AS question JOIN conversations ON conversations.id=question.conversation_id "
            "JOIN chat_turns AS turns ON turns.conversation_id=question.conversation_id AND turns.request_id=question.request_id "
            "LEFT JOIN messages AS answer ON answer.conversation_id=question.conversation_id AND answer.request_id=question.request_id AND answer.role='assistant' "
            "WHERE conversations.user_mail=? AND question.role='user' AND turns.state='completed' "
            "ORDER BY turns.completed_at DESC, question.sequence DESC LIMIT ? OFFSET ?",
            (mail, limit, offset),
        )
        activity = []
        for row in items:
            classification = json.loads(row["classification"]) if row["classification"] else None
            activity.append({
                "prompt": row["prompt"],
                "createdAt": row["created_at"],
                "classification": classification,
                "providerId": row["provider_id"],
                "modelId": row["model_id"],
                "durationSeconds": round(float(row["duration_seconds"] or 0)),
                "conversationId": row["conversation_id"],
                "conversationTitle": row["title"],
            })
        return {
            "limits": lock,
            "summary": {
                "totalQueries": total,
                "personalQueries": int(totals["personal"] or 0),
                "classifiedQueries": int(totals["classified"] or 0),
                "categoryCounts": category_counts,
                "providerCounts": [{"providerId": row["provider_id"], "count": int(row["count"])} for row in by_provider],
                "lastSevenDays": [{"date": row["day"], "count": int(row["count"]), "personal": int(row["personal"] or 0)} for row in daily],
            },
            "activity": {"items": activity, "total": total, "offset": offset, "limit": limit, "hasMore": offset + len(activity) < total},
        }
