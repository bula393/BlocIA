import pytest

from app.domain.user.user import User


def test_profile_update_validates_changed_values():
    user = User(mail="user@example.com", age=20, profession="Estudiante")
    user.update_profile(age=21, profession="Docente", display_name="Usuario")
    assert user.age == 21
    assert user.profession == "Docente"
    with pytest.raises(ValueError):
        user.update_profile(age=0)
    with pytest.raises(ValueError):
        user.update_profile(profession="")
