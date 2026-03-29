"""Base use case abstractions for commands and queries."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class BaseCommand(ABC, Generic[TInput, TOutput]):
    """Abstract base class for command use cases.

    Commands perform side effects (create, update, delete).

    Type Args:
        TInput: The input DTO type.
        TOutput: The output DTO type.
    """

    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        """Execute the command.

        Args:
            input_data: The command input DTO.

        Returns:
            The command output DTO.
        """


class BaseQuery(ABC, Generic[TInput, TOutput]):
    """Abstract base class for query use cases.

    Queries are read-only and must not cause side effects.

    Type Args:
        TInput: The input DTO type.
        TOutput: The output DTO type.
    """

    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        """Execute the query.

        Args:
            input_data: The query input DTO.

        Returns:
            The query output DTO.
        """
