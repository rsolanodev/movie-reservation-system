from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.movies.actions.retrieve_all_movies import RetrieveAllMovies
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.factories.movie_factory import MovieFactory


class TestRetrieveAllMovies:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_retrieves_all_movies(self, mock_repository: Mock) -> None:
        expected_movies = [MovieFactory().create()]
        mock_repository.get_all.return_value = expected_movies

        movies = RetrieveAllMovies(repository=mock_repository).execute()

        mock_repository.get_all.assert_called_once()

        assert movies == expected_movies
