"""SMTP delivery with mandatory TLS and no credential/code logging."""

from email.message import EmailMessage
from email.utils import parseaddr
import os
import smtplib
import ssl

from app.application.user.verify_email import EmailVerificationError


class SmtpEmailSender:
    def send_verification(self, recipient: str, code: str, expires_seconds: int):
        host = os.getenv("SMTP_HOST", "").strip()
        username = os.getenv("SMTP_USERNAME", "").strip()
        password = os.getenv("SMTP_PASSWORD", "")
        sender = os.getenv("SMTP_FROM", "").strip()
        security = os.getenv("SMTP_SECURITY", "starttls").strip().lower()
        if not all((host, username, password, sender)):
            raise EmailVerificationError("El envío de códigos todavía no está configurado. Contactá al administrador.", 503)
        try:
            port = int(os.getenv("SMTP_PORT", "465" if security == "ssl" else "587"))
            if security not in ("starttls", "ssl") or not 1 <= port <= 65535:
                raise ValueError("Invalid SMTP transport")
            if any(character in sender + recipient for character in "\r\n") or "@" not in parseaddr(sender)[1]:
                raise ValueError("Invalid SMTP sender")
            message = EmailMessage()
            message["Subject"] = "Tu código de verificación de BloqIA"
            message["From"], message["To"] = sender, recipient
            message.set_content(
                f"Tu código para verificar tu cuenta de BloqIA es: {code}\n\n"
                f"Vence en {expires_seconds // 60} minutos y permite conectar tus propias claves de IA.\n"
                "Si no lo pediste, podés ignorar este correo. No compartas el código.\n"
            )
            context = ssl.create_default_context()
            transport = smtplib.SMTP_SSL(host, port, timeout=10, context=context) if security == "ssl" else smtplib.SMTP(host, port, timeout=10)
            with transport as smtp:
                if security == "starttls":
                    smtp.ehlo()
                    smtp.starttls(context=context)
                    smtp.ehlo()
                smtp.login(username, password)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException, ValueError):
            raise EmailVerificationError("No pudimos enviar el código. Intentá de nuevo más tarde.", 503) from None
