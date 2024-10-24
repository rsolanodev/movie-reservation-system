from datetime import date, datetime, timezone
from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest
from freezegun import freeze_time

from app.movies.application.retrieve_movie import RetrieveMovie, RetrieveMovieParams
from app.movies.domain.collections.movie_genres import MovieGenres
from app.movies.domain.collections.movie_showtimes import MovieShowtimes
from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.domain.movie_showtime import MovieShowtime
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.factories.genre_factory_test import GenreFactoryTest
from app.movies.tests.factories.movie_showtime_factory_test import (
    MovieShowtimeFactoryTest,
)
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


@freeze_time("2023-04-03T22:00:00Z")
class TestRetrieveMovie:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_retrieves_movie(self, mock_repository: Mock) -> None:
        mock_repository.get_movie_for_date.return_value = (
            MovieBuilder()
            .with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_title("The Super Mario Bros. Movie")
            .with_description("An animated adaptation of the video game.")
            .with_poster_image("super_mario_bros.jpg")
            .with_genre(
                genre=GenreFactoryTest().create(
                    id=UUID("c8693e5a-ac9c-4560-9970-7ae4f22ddf0a"),
                    name="Adventure",
                )
            )
            .with_showtime(
                showtime=MovieShowtimeFactoryTest().create(
                    id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                    show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                )
            )
            .build()
        )

        movie = RetrieveMovie(repository=mock_repository).execute(
            params=RetrieveMovieParams(
                movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                showtime_date=date(2023, 4, 3),
            )
        )

        mock_repository.get_movie_for_date.assert_called_once_with(
            movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            showtime_date=date(2023, 4, 3),
        )
        assert movie == Movie(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            title="The Super Mario Bros. Movie",
            description="An animated adaptation of the video game.",
            poster_image="super_mario_bros.jpg",
            genres=MovieGenres([Genre(id=UUID("c8693e5a-ac9c-4560-9970-7ae4f22ddf0a"), name="Adventure")]),
            showtimes=MovieShowtimes(
                [
                    MovieShowtime(
                        id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                        show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                    )
                ],
            ),
        )

    def test_raise_exception_when_movie_does_not_exist(self, mock_repository: Mock) -> None:
        mock_repository.get_movie_for_date.return_value = None

        with pytest.raises(MovieDoesNotExist):
            RetrieveMovie(repository=mock_repository).execute(
                params=RetrieveMovieParams(
                    movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                    showtime_date=date(2023, 4, 3),
                )
            )

        mock_repository.get_movie_for_date.assert_called_once_with(
            movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            showtime_date=date(2023, 4, 3),
        )
