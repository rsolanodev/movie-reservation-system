from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.movies.application.commands.add_movie_genre import AddMovieGenre, AddMovieGenreParams
from app.movies.domain.exceptions import GenreAlreadyAssigned
from app.movies.domain.finders.movie_finder import MovieFinder
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.domain.mothers.genre_mother import GenreMother
from app.shared.domain.value_objects.id import Id
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestAddMovieGenre:
    @pytest.fixture
    def mock_movie_repository(self) -> Any:
        return create_autospec(spec=MovieRepository, instance=True, spec_set=True)

    @pytest.fixture
    def mock_movie_finder(self) -> Any:
        return create_autospec(spec=MovieFinder, instance=True, spec_set=True)

    def test_adds_genre_to_movie(self, mock_movie_repository: Mock, mock_movie_finder: Mock) -> None:
        movie = MovieBuilder().build()
        genre = GenreMother().with_name("Action").create()

        mock_movie_finder.find_movie.return_value = movie

        AddMovieGenre(repository=mock_movie_repository, finder=mock_movie_finder).execute(
            params=AddMovieGenreParams(movie_id=movie.id, genre_id=genre.id)
        )

        mock_movie_finder.find_movie.assert_called_once_with(movie_id=movie.id)
        mock_movie_repository.add_genre.assert_called_once_with(movie_id=movie.id, genre_id=genre.id)

    def test_raise_exception_when_genre_is_already_assigned_in_movie(
        self, mock_movie_repository: Mock, mock_movie_finder: Mock
    ) -> None:
        movie = MovieBuilder().with_genre(GenreMother().create()).build()
        mock_movie_finder.find_movie.return_value = movie

        with pytest.raises(GenreAlreadyAssigned):
            AddMovieGenre(repository=mock_movie_repository, finder=mock_movie_finder).execute(
                params=AddMovieGenreParams(movie_id=movie.id, genre_id=Id("c8693e5a-ac9c-4560-9970-7ae4f22ddf0a"))
            )

        mock_movie_finder.find_movie.assert_called_once_with(movie_id=movie.id)
        mock_movie_repository.add_genre.assert_not_called()
