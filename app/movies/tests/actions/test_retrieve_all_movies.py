from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

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

    def test_retrieves_movies_filtered_by_genre(self, mock_repository: Mock) -> None:
        expected_movies = [MovieFactory().create_with_genre()]
        mock_repository.get_all.return_value = expected_movies

        movies = RetrieveAllMovies(repository=mock_repository).execute(
            genre_id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9")
        )

        mock_repository.get_all.assert_called_once()

        assert movies == expected_movies

    def test_retrieves_movies_filtered_by_genre_that_does_not_exist(
        self, mock_repository: Mock
    ) -> None:
        mock_repository.get_all.return_value = [MovieFactory().create_with_genre()]

        movies = RetrieveAllMovies(repository=mock_repository).execute(
            genre_id=UUID("e219f84b-3568-446b-896c-3ba2bc74ceb0")
        )

        mock_repository.get_all.assert_called_once()

        assert movies == []
