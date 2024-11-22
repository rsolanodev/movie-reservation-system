from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.movies.application.add_movie_genre import AddMovieGenre
from app.movies.domain.exceptions import GenreAlreadyAssigned
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.factories.genre_factory_test import GenreFactoryTest
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestAddMovieGenre:
    @pytest.fixture
    def mock_movie_repository(self) -> Any:
        return create_autospec(spec=MovieRepository, instance=True, spec_set=True)

    def test_adds_genre_to_movie(self, mock_movie_repository: Mock) -> None:
        movie = MovieBuilder().build()
        genre = GenreFactoryTest().create(name="Action")

        mock_movie_repository.get.return_value = movie

        AddMovieGenre(repository=mock_movie_repository).execute(movie_id=movie.id, genre_id=genre.id)

        mock_movie_repository.get.assert_called_once_with(id=movie.id)
        mock_movie_repository.add_genre.assert_called_once_with(movie_id=movie.id, genre_id=genre.id)

    def test_raise_exception_when_genre_is_already_assigned_in_movie(self, mock_movie_repository: Mock) -> None:
        movie = (
            MovieBuilder()
            .with_genre(
                genre=GenreFactoryTest().create(
                    id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                    name="Action",
                )
            )
            .build()
        )

        mock_movie_repository.get.return_value = movie

        with pytest.raises(GenreAlreadyAssigned):
            AddMovieGenre(repository=mock_movie_repository).execute(
                movie_id=movie.id, genre_id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9")
            )

        mock_movie_repository.get.assert_called_once_with(id=movie.id)
        mock_movie_repository.add_genre.assert_not_called()
