from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.movies.actions.delete_movie import DeleteMovie
from app.movies.domain.exceptions import MovieDoesNotExistException
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestDeleteMovie:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_deletes_movie(self, mock_repository: Mock) -> None:
        mock_repository.get.return_value = (
            MovieBuilder().with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")).build()
        )

        DeleteMovie(repository=mock_repository).execute(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))

        mock_repository.get.assert_called_once_with(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
        mock_repository.delete.assert_called_once_with(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))

    def test_raise_exception_when_movie_does_not_exist(self, mock_repository: Mock) -> None:
        mock_repository.get.return_value = None

        with pytest.raises(MovieDoesNotExistException):
            DeleteMovie(repository=mock_repository).execute(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))

        mock_repository.get.assert_called_once_with(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
        mock_repository.delete.assert_not_called()
