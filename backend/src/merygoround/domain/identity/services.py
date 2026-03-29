"""Domain service interfaces for the Identity bounded context."""

from __future__ import annotations

from abc import ABC, abstractmethod


class PasswordHashingService(ABC):
    """Abstract service for password hashing and verification."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a plaintext password.

        Args:
            password: The plaintext password to hash.

        Returns:
            The hashed password string.
        """

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a hash.

        Args:
            plain_password: The plaintext password to verify.
            hashed_password: The stored hash to compare against.

        Returns:
            True if the password matches the hash, False otherwise.
        """
