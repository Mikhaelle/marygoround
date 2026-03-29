"""JWT token creation and verification service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt


class JWTService:
    """Service for creating and verifying JSON Web Tokens.

    Args:
        secret_key: The secret key for signing tokens.
        algorithm: The JWT signing algorithm (default: HS256).
        access_token_expire_minutes: Access token TTL in minutes (default: 30).
        refresh_token_expire_days: Refresh token TTL in days (default: 7).
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(self, subject: str) -> str:
        """Create a short-lived access token.

        Args:
            subject: The token subject (typically user ID).

        Returns:
            The encoded JWT string.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._access_token_expire_minutes
        )
        payload = {
            "sub": subject,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, subject: str) -> str:
        """Create a long-lived refresh token.

        Args:
            subject: The token subject (typically user ID).

        Returns:
            The encoded JWT string.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            days=self._refresh_token_expire_days
        )
        payload = {
            "sub": subject,
            "exp": expire,
            "type": "refresh",
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> str | None:
        """Verify a JWT token and extract the subject.

        Args:
            token: The encoded JWT string.
            token_type: Expected token type ("access" or "refresh").

        Returns:
            The subject string if valid, otherwise None.
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            if payload.get("type") != token_type:
                return None
            subject: str | None = payload.get("sub")
            return subject
        except JWTError:
            return None
