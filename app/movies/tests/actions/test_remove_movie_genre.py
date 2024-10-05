from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.movies.actions.remove_movie_genre import RemoveMovieGenre
from app.movies.domain.exceptions import GenreNotAssignedException
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.domain.factories.genre_factory import GenreFactory
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestRemoveMovieGenre:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_removes_genre_from_movie(self, mock_repository: Mock) -> None:
        movie = (
            MovieBuilder()
            .with_genre(
                genre=GenreFactory().create(
                    id=UUID("3b74494d-0a95-49b1-91ef-bb211f802961"), name="Action"
                )
            )
            .build()
        )

        mock_repository.get.return_value = movie

        RemoveMovieGenre(repository=mock_repository).execute(
            movie_id=movie.id, genre_id=UUID("3b74494d-0a95-49b1-91ef-bb211f802961")
        )

        mock_repository.get.assert_called_once_with(id=movie.id)
        mock_repository.remove_genre.assert_called_once_with(
            movie_id=movie.id, genre_id=UUID("3b74494d-0a95-49b1-91ef-bb211f802961")
        )

    def test_raise_exception_when_genre_is_not_assigned_in_movie(
        self, mock_repository: Mock
    ) -> None:
        movie = MovieBuilder().build()
        mock_repository.get.return_value = movie

        with pytest.raises(GenreNotAssignedException):
            RemoveMovieGenre(repository=mock_repository).execute(
                movie_id=movie.id, genre_id=UUID("3b74494d-0a95-49b1-91ef-bb211f802961")
            )

        mock_repository.get.assert_called_once_with(id=movie.id)
        mock_repository.remove_genre.assert_not_called()
