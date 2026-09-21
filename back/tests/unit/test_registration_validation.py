import pytest

from app.domain.user.user import User


def test_user_required_fields_validation():
    User(mail="valid@example.com", age=1, profession="Estudiante").validate()
    with pytest.raises(ValueError):
        User(mail="invalid", age=1, profession="Estudiante").validate()
    with pytest.raises(ValueError):
        User(mail="valid@example.com", age=0, profession="Estudiante").validate()
    with pytest.raises(ValueError):
        User(mail="valid@example.com", age=1, profession="").validate()
