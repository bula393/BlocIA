"""Exercise mail delivery through fake transports; no SMTP server is contacted."""

import smtplib
import ssl

import pytest

from app.application.user.verify_email import EmailVerificationError
from app.infrastructure.user import smtp_email_sender as delivery


RECIPIENT = "ownership@example.com"
CODE = "037291"
USERNAME = "smtp-account-private"
PASSWORD = "smtp-password-private"


@pytest.fixture
def smtp(monkeypatch):
    for key in ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM", "SMTP_PORT", "SMTP_SECURITY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_USERNAME", USERNAME)
    monkeypatch.setenv("SMTP_PASSWORD", PASSWORD)
    monkeypatch.setenv("SMTP_FROM", "BloqIA <noreply@example.com>")
    events, messages, connections = [], [], []
    failure = {}

    def event(name, value=None):
        events.append(name)
        if failure.get("stage") == name:
            raise failure["error"]
        return value

    class Transport:
        def __enter__(self):
            return event("enter", self)

        def __exit__(self, *args):
            event("exit")

        def ehlo(self):
            event("ehlo")

        def starttls(self, *, context):
            connections[-1][2]["tls_context"] = context
            event("starttls")

        def login(self, username, password):
            assert username == USERNAME and password == PASSWORD
            event("login")

        def send_message(self, message):
            event("send_message")
            messages.append(message)
            return {}

    def factory(kind):
        def connect(*args, **kwargs):
            connections.append((kind, args, kwargs))
            event("connect_" + kind)
            return Transport()
        return connect

    monkeypatch.setattr(delivery.smtplib, "SMTP", factory("starttls"))
    monkeypatch.setattr(delivery.smtplib, "SMTP_SSL", factory("ssl"))
    return events, messages, connections, failure


@pytest.mark.parametrize("security,port", [("starttls", 587), ("SSL", 465)])
def test_delivery_uses_verified_tls_before_authentication_and_does_not_log_secrets(
    monkeypatch, smtp, caplog, capsys, security, port
):
    monkeypatch.setenv("SMTP_SECURITY", security)
    events, messages, connections, _ = smtp
    delivery.SmtpEmailSender().send_verification(RECIPIENT, CODE, 600)

    kind, args, kwargs = connections[0]
    assert kind == security.lower()
    assert args == ("smtp.example.com", port) and kwargs["timeout"] == 10
    context = kwargs["context"] if kind == "ssl" else kwargs["tls_context"]
    assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
    expected = ["connect_starttls", "enter", "ehlo", "starttls", "ehlo", "login", "send_message", "exit"]
    if kind == "ssl":
        expected = ["connect_ssl", "enter", "login", "send_message", "exit"]
    assert events == expected
    assert len(messages) == 1
    message = messages[0]
    assert str(message["To"]) == RECIPIENT
    assert str(message["From"]) == "BloqIA <noreply@example.com>"
    assert CODE in message.get_content() and "10 minutos" in message.get_content()
    captured_output = capsys.readouterr()
    output = caplog.text + captured_output.out + captured_output.err
    assert all(secret not in output for secret in (CODE, USERNAME, PASSWORD))


def test_default_transport_is_starttls_and_custom_port_is_respected(monkeypatch, smtp):
    monkeypatch.setenv("SMTP_PORT", "2525")
    delivery.SmtpEmailSender().send_verification(RECIPIENT, CODE, 600)
    assert smtp[2][0][0:2] == ("starttls", ("smtp.example.com", 2525))


@pytest.mark.parametrize("field", ["SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM"])
def test_incomplete_configuration_fails_before_any_connection(monkeypatch, smtp, field):
    monkeypatch.delenv(field)
    with pytest.raises(EmailVerificationError) as captured:
        delivery.SmtpEmailSender().send_verification(RECIPIENT, CODE, 600)
    assert captured.value.status_code == 503 and not smtp[2]


@pytest.mark.parametrize("field,value", [
    ("SMTP_SECURITY", "none"), ("SMTP_SECURITY", "plain"),
    ("SMTP_PORT", "bad"), ("SMTP_PORT", "0"), ("SMTP_PORT", "65536"),
    ("SMTP_FROM", "invalid-address"), ("SMTP_FROM", "valid@example.com\r\nBcc: other@example.com"),
])
def test_invalid_configuration_fails_closed_without_network(monkeypatch, smtp, field, value):
    monkeypatch.setenv(field, value)
    with pytest.raises(EmailVerificationError) as captured:
        delivery.SmtpEmailSender().send_verification(RECIPIENT, CODE, 600)
    assert captured.value.status_code == 503 and not smtp[2]
    assert captured.value.__suppress_context__


def test_recipient_header_injection_fails_before_connection(smtp):
    with pytest.raises(EmailVerificationError) as captured:
        delivery.SmtpEmailSender().send_verification(RECIPIENT + "\nBcc: attacker@example.com", CODE, 600)
    assert captured.value.status_code == 503 and not smtp[2]


@pytest.mark.parametrize("security,stage,error", [
    ("starttls", "connect_starttls", smtplib.SMTPConnectError(421, b"private server details")),
    ("ssl", "connect_ssl", ssl.SSLCertVerificationError("private certificate details")),
    ("starttls", "ehlo", smtplib.SMTPServerDisconnected("private server details")),
    ("starttls", "starttls", smtplib.SMTPNotSupportedError("TLS unavailable")),
    ("starttls", "starttls", ssl.SSLError("TLS handshake rejected")),
    ("starttls", "login", smtplib.SMTPAuthenticationError(535, PASSWORD.encode())),
    ("ssl", "login", smtplib.SMTPAuthenticationError(535, PASSWORD.encode())),
    ("starttls", "send_message", smtplib.SMTPRecipientsRefused({RECIPIENT: (550, CODE.encode())})),
    ("ssl", "send_message", OSError(PASSWORD + " " + CODE)),
    ("ssl", "exit", smtplib.SMTPServerDisconnected("private server details")),
])
def test_transport_failure_is_sanitized_and_never_falls_back_to_plaintext(
    monkeypatch, smtp, caplog, capsys, security, stage, error
):
    monkeypatch.setenv("SMTP_SECURITY", security)
    events, _, connections, failure = smtp
    failure.update(stage=stage, error=error)
    with pytest.raises(EmailVerificationError) as captured:
        delivery.SmtpEmailSender().send_verification(RECIPIENT, CODE, 600)
    assert captured.value.status_code == 503
    assert str(captured.value) == "No pudimos enviar el código. Intentá de nuevo más tarde."
    assert captured.value.__suppress_context__ and captured.value.__cause__ is None
    assert len(connections) == 1
    if stage in ("connect_starttls", "connect_ssl", "ehlo", "starttls"):
        assert "login" not in events and "send_message" not in events
    captured_output = capsys.readouterr()
    output = str(captured.value) + caplog.text + captured_output.out + captured_output.err
    assert all(secret not in output for secret in (CODE, USERNAME, PASSWORD, "private server details", "private certificate details"))
