import pytest

from app.domain.user.password_policy import PasswordPolicy


def test_password_policy_rules():
    PasswordPolicy.validate("ClaveSegura-123", "user@example.com")
    with pytest.raises(ValueError):
        PasswordPolicy.validate("123", "user@example.com")
    with pytest.raises(ValueError):
        PasswordPolicy.validate("user-Password123", "user@example.com")


def test_password_hashes_use_random_salt_and_slow_pbkdf2():
    first = PasswordPolicy.hash_password("ClaveSegura-123")
    second = PasswordPolicy.hash_password("ClaveSegura-123")

    assert first != second
    assert first.startswith("pbkdf2_sha256$600000$")
    assert PasswordPolicy.verify("ClaveSegura-123", first)
    assert not PasswordPolicy.verify("ClaveIncorrecta-123", first)
    assert not PasswordPolicy.verify("ClaveSegura-123", "pbkdf2_sha256$999999999$bad$bad")


def test_legacy_sha256_is_verified_then_marked_for_upgrade():
    import hashlib

    legacy = hashlib.sha256("ClaveSegura-123".encode()).hexdigest()
    assert PasswordPolicy.verify("ClaveSegura-123", legacy)
    assert PasswordPolicy.needs_rehash(legacy)
