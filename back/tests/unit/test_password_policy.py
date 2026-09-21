import pytest

from app.domain.user.password_policy import PasswordPolicy


def test_password_policy_rules():
    PasswordPolicy.validate("ClaveSegura-123", "user@example.com")
    with pytest.raises(ValueError):
        PasswordPolicy.validate("123", "user@example.com")
    with pytest.raises(ValueError):
        PasswordPolicy.validate("user-Password123", "user@example.com")
