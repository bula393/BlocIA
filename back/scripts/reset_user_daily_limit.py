"""Reset one BloqIA account's rolling 24-hour usage limit and active lock.

Run from ``back`` with the backend's Python environment:
    python scripts/reset_user_daily_limit.py

The script retains conversation and usage history. It writes a per-account
reset timestamp so prior usage no longer counts toward the rolling limit.
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import sys


BACK_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACK_DIR))

from app.infrastructure.database import Database, ROOT  # noqa: E402


def main() -> int:
    database_url = os.getenv("DATABASE_URL")
    database_path = Path(os.getenv("BLOCIA_DATABASE_PATH", str(ROOT / "data/blocia.sqlite3")))
    if not database_url and not database_path.is_file():
        print(f"No encuentro la base de datos: {database_path}")
        return 1

    mail = input("Correo de la cuenta que querés reiniciar: ").strip()
    if not mail or "@" not in mail:
        print("Ingresá un correo válido.")
        return 1

    reason = input("Motivo del reinicio: ").strip()
    if not reason:
        print("El motivo es obligatorio para dejar registro de la acción.")
        return 1

    try:
        database = Database(database_path, legacy_path=None, database_url=database_url)
    except Exception as error:
        print(f"No se pudo conectar a la base de datos ({type(error).__name__}).")
        return 1
    try:
        with database.transaction():
            users = database.query("SELECT mail FROM users WHERE lower(mail)=lower(?) LIMIT 2", (mail,))
        if len(users) != 1:
            print("No encontré una cuenta única con ese correo.")
            return 1

        account_mail = users[0]["mail"]
        print(f"Cuenta seleccionada: {account_mail}")
        confirmation = input(
            f"Escribí RESET para confirmar (o RESET {account_mail}): "
        ).strip().casefold()
        accepted_confirmations = {"reset", f"reset {account_mail}".casefold()}
        if confirmation not in accepted_confirmations:
            print("Cancelado. Escribí RESET para confirmar; no se modificó la cuenta.")
            return 1

        reset_at = datetime.now(timezone.utc).timestamp()
        with database.transaction():
            database.execute(
                "INSERT INTO user_usage_resets(user_mail, reset_at, reason) VALUES (?, ?, ?)",
                (account_mail, reset_at, reason),
            )
            database.execute("DELETE FROM user_usage_locks WHERE user_mail=?", (account_mail,))
        print(f"Límite reiniciado y bloqueo quitado para {account_mail}.")
        print(f"Fecha UTC: {datetime.fromtimestamp(reset_at, timezone.utc).isoformat()}")
        print("El historial de chats y uso quedó intacto.")
        return 0
    except Exception as error:
        print(f"No se pudo completar el reinicio ({type(error).__name__}).")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
