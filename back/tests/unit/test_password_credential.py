from app.domain.user.password_credential import PasswordCredential


def test_password_hash_is_non_displayable_and_invalid_attempt_does_not_lock():
    credential = PasswordCredential.create("user@example.com", "ClaveSegura-123")

    assert credential.password_hash != "ClaveSegura-123"
    assert credential.verify("ClaveSegura-123")
    assert credential.register_invalid_attempt() is None
    assert credential.verify("ClaveSegura-123")
