"""Bcrypt implementation of the PasswordHashingService."""

from __future__ import annotations

import bcrypt

from merygoround.domain.identity.services import PasswordHashingService


class BcryptPasswordHashingService(PasswordHashingService):
    """Password hashing service using bcrypt directly."""

    def hash_password(self, password: str) -> str:
        """Hash a plaintext password using bcrypt.

        Args:
            password: The plaintext password to hash.

        Returns:
            The bcrypt-hashed password string.
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a bcrypt hash.

        Args:
            plain_password: The plaintext password to verify.
            hashed_password: The stored bcrypt hash to compare against.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
