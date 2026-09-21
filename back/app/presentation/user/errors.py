from fastapi import HTTPException


def error_response(message: str, status_code: int = 400) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"message": message})


def validation_error_response(message: str, fields: dict[str, str]) -> HTTPException:
    return HTTPException(status_code=400, detail={"message": message, "fields": fields})
