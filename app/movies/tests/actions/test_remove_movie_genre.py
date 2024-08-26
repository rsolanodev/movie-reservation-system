from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.movies.actions.remove_movie_genre import RemoveMovieGenre
from app.movies.domain.exceptions import GenreNotAssignedException
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.factories.genre_factory import GenreFactory
from app.movies.tests.factories.movie_factory import MovieFactory


class TestRemoveMovieGenre:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_removes_genre_from_movie(self, mock_repository: Mock) -> None:
        movie = MovieFactory().create()
        genre = GenreFactory().create()
        movie.add_genre(genre=genre)

        mock_repository.get.return_value = movie

        RemoveMovieGenre(repository=mock_repository).execute(
            movie_id=movie.id, genre_id=genre.id
        )

        mock_repository.get.assert_called_once_with(id=movie.id)
        mock_repository.remove_genre.assert_called_once_with(
            movie_id=movie.id, genre_id=genre.id
        )

    def test_raise_exception_when_genre_is_not_assigned_in_movie(
        self, mock_repository: Mock
    ) -> None:
        movie = MovieFactory().create()
        mock_repository.get.return_value = movie

        with pytest.raises(GenreNotAssignedException):
            RemoveMovieGenre(repository=mock_repository).execute(
                movie_id=movie.id, genre_id=UUID("3b74494d-0a95-49b1-91ef-bb211f802961")
            )

        mock_repository.get.assert_called_once_with(id=movie.id)
        mock_repository.remove_genre.assert_not_called()
