import re


def redact_personal_data(text: str) -> str:
    """Best-effort redaction of explicit identifiers before history persistence."""
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", "[CORREO]", text)
    text = re.sub(r"(?<!\w)(?:\+?\d[\s().-]*){8,15}(?!\w)", "[TELÉFONO]", text)
    text = re.sub(r"(?i)\b(me llamo|mi nombre es)\s+[^\W\d_]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3}", r"\1 [NOMBRE]", text)
    text = re.sub(r"(?i)\b(mi direcci[oó]n es|vivo en la calle|domicilio:)\s*[^\n;!?]+", r"\1 [DIRECCIÓN]", text)
    return text
