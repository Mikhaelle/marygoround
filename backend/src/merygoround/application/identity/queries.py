"""Query use cases for the Identity bounded context."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from merygoround.application.identity.dtos import UserResponse
from merygoround.application.shared.use_case import BaseQuery
from merygoround.domain.identity.exceptions import UserNotFoundError

if TYPE_CHECKING:
    from merygoround.domain.identity.repository import UserRepository


class GetCurrentUserQuery(BaseQuery[uuid.UUID, UserResponse]):
    """Retrieves the current authenticated user's profile.

    Args:
        user_repo: User repository for lookup.
    """

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, input_data: uuid.UUID) -> UserResponse:
        """Look up the user by their ID.

        Args:
            input_data: The UUID of the authenticated user.

        Returns:
            UserResponse with the user's profile data.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
        user = await self._user_repo.get_by_id(input_data)
        if user is None:
            raise UserNotFoundError(str(input_data))

        return UserResponse(id=user.id, email=user.email.value, name=user.name)
