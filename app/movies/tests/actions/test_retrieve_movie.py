from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.movies.actions.retrieve_movie import RetrieveMovie
from app.movies.domain.exceptions import MovieDoesNotExistException
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.domain.factories.genre_factory import GenreFactory
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestRetrieveMovie:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_retrieves_movie(self, mock_repository: Mock) -> None:
        movie = (
            MovieBuilder()
            .with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_genre(genre=GenreFactory().create(name="Comedy"))
            .build()
        )
        mock_repository.get.return_value = movie

        result = RetrieveMovie(repository=mock_repository).execute(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )

        mock_repository.get.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
        assert result == movie

    def test_raise_exception_when_movie_does_not_exist(
        self, mock_repository: Mock
    ) -> None:
        mock_repository.get.return_value = None

        with pytest.raises(MovieDoesNotExistException):
            RetrieveMovie(repository=mock_repository).execute(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
            )

        mock_repository.get.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
