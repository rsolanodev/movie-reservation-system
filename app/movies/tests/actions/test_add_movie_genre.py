from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.movies.actions.add_movie_genre import AddMovieGenre
from app.movies.domain.exceptions import GenreAlreadyAssignedException
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.factories.genre_factory import GenreFactory
from app.movies.tests.factories.movie_factory import MovieFactory


class TestAddMovieGenre:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_adds_genre_to_movie(self, mock_repository: Mock) -> None:
        movie = MovieFactory().create()
        genre = GenreFactory().create()

        mock_repository.get.return_value = movie

        AddMovieGenre(repository=mock_repository).execute(
            movie_id=movie.id, genre_id=genre.id
        )

        mock_repository.get.assert_called_once_with(id=movie.id)
        mock_repository.add_genre.assert_called_once_with(
            movie_id=movie.id, genre_id=genre.id
        )

    def test_raise_exception_when_genre_is_already_assigned_in_movie(
        self, mock_repository: Mock
    ) -> None:
        movie = MovieFactory().create()
        genre = GenreFactory().create()
        movie.add_genre(genre=genre)

        mock_repository.get.return_value = movie

        with pytest.raises(GenreAlreadyAssignedException):
            AddMovieGenre(repository=mock_repository).execute(
                movie_id=movie.id, genre_id=genre.id
            )

        mock_repository.get.assert_called_once_with(id=movie.id)
        mock_repository.add_genre.assert_not_called()
