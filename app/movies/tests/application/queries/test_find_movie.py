from datetime import date, datetime
from typing import Any
from unittest.mock import Mock, create_autospec

import pytest
from freezegun import freeze_time

from app.movies.application.queries.find_movie import FindMovie, FindMovieParams
from app.movies.domain.collections.movie_genres import MovieGenres
from app.movies.domain.collections.movie_showtimes import MovieShowtimes
from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.finders.movie_finder import MovieFinder
from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.domain.movie_showtime import MovieShowtime
from app.movies.tests.domain.mothers.genre_mother import GenreMother
from app.movies.tests.domain.mothers.movie_showtime_mother import MovieShowtimeMother
from app.shared.domain.value_objects.date import Date
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


@freeze_time("2023-04-03T22:00:00Z")
class TestFindMovie:
    @pytest.fixture
    def mock_movie_finder(self) -> Any:
        return create_autospec(spec=MovieFinder, instance=True, spec_set=True)

    def test_find_movie(self, mock_movie_finder: Mock) -> None:
        mock_movie_finder.find_movie_by_showtime_date.return_value = (
            MovieBuilder()
            .with_id(id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_title("The Super Mario Bros. Movie")
            .with_description("An animated adaptation of the video game.")
            .with_poster_image("super_mario_bros.jpg")
            .with_genre(GenreMother().create())
            .with_showtime(MovieShowtimeMother().create())
            .build()
        )

        movie = FindMovie(finder=mock_movie_finder).execute(
            params=FindMovieParams(
                movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                showtime_date=Date.from_datetime_date(date(2023, 4, 3)),
            )
        )

        mock_movie_finder.find_movie_by_showtime_date.assert_called_once_with(
            movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            showtime_date=Date.from_datetime_date(date(2023, 4, 3)),
        )

        assert movie == Movie(
            id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            title="The Super Mario Bros. Movie",
            description="An animated adaptation of the video game.",
            poster_image="super_mario_bros.jpg",
            genres=MovieGenres([Genre(id=Id("c8693e5a-ac9c-4560-9970-7ae4f22ddf0a"), name="Adventure")]),
            showtimes=MovieShowtimes(
                [
                    MovieShowtime(
                        id=Id("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                        show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                    )
                ],
            ),
        )

    def test_raise_exception_when_movie_does_not_exist(self, mock_movie_finder: Mock) -> None:
        mock_movie_finder.find_movie_by_showtime_date.return_value = None

        with pytest.raises(MovieDoesNotExist):
            FindMovie(finder=mock_movie_finder).execute(
                params=FindMovieParams(
                    movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                    showtime_date=Date.from_datetime_date(date(2023, 4, 3)),
                )
            )

        mock_movie_finder.find_movie_by_showtime_date.assert_called_once_with(
            movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            showtime_date=Date.from_datetime_date(date(2023, 4, 3)),
        )
