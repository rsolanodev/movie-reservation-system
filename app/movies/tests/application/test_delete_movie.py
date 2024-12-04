from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.movies.application.delete_movie import DeleteMovie
from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.domain.value_objects.id import ID
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestDeleteMovie:
    @pytest.fixture
    def mock_movie_repository(self) -> Any:
        return create_autospec(spec=MovieRepository, instance=True, spec_set=True)

    def test_deletes_movie(self, mock_movie_repository: Mock) -> None:
        movie = MovieBuilder().build()
        mock_movie_repository.get.return_value = movie

        DeleteMovie(repository=mock_movie_repository).execute(id=movie.id)

        mock_movie_repository.get.assert_called_once_with(id=movie.id)
        mock_movie_repository.delete.assert_called_once_with(id=movie.id)

    def test_raise_exception_when_movie_does_not_exist(self, mock_movie_repository: Mock) -> None:
        movie_id = ID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        mock_movie_repository.get.return_value = None

        with pytest.raises(MovieDoesNotExist):
            DeleteMovie(repository=mock_movie_repository).execute(id=movie_id)

        mock_movie_repository.get.assert_called_once_with(id=movie_id)
        mock_movie_repository.delete.assert_not_called()
