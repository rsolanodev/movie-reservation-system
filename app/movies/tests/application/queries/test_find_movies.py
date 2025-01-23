from datetime import date, datetime
from typing import Any
from unittest.mock import Mock, create_autospec

import pytest
from freezegun import freeze_time

from app.movies.application.queries.find_movies import FindMovies, FindMoviesParams
from app.movies.domain.collections.movie_genres import MovieGenres
from app.movies.domain.collections.movie_showtimes import MovieShowtimes
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
class TestFindMovies:
    @pytest.fixture
    def mock_movie_finder(self) -> Any:
        return create_autospec(spec=MovieFinder, instance=True, spec_set=True)

    @pytest.fixture
    def showtime_date(self) -> Date:
        return Date.from_datetime_date(date(2023, 4, 3))

    @pytest.fixture
    def movies(self) -> list[Movie]:
        return [
            MovieBuilder()
            .with_id(Id("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_title("Deadpool & Wolverine")
            .with_description("Deadpool and a variant of Wolverine.")
            .with_poster_image("deadpool_and_wolverine.jpg")
            .with_genre(GenreMother().with_id(Id("d108f84b-3568-446b-896c-3ba2bc74cda8")).with_name("Comedy").create())
            .with_showtime(
                MovieShowtimeMother()
                .with_id(Id("b6439a2d-c0c0-45c8-81b7-7d7b155830ba"))
                .with_show_datetime(DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)))
                .create()
            )
            .build(),
            MovieBuilder()
            .with_id(Id("ec725625-f502-4d39-9401-a415d8c1f965"))
            .with_title("The Super Mario Bros. Movie")
            .with_description("An animated adaptation of the video game.")
            .with_poster_image("super_mario_bros.jpg")
            .with_genre(
                GenreMother().with_id(Id("d108f84b-3568-446b-896c-3ba2bc74cda9")).with_name("Adventure").create()
            )
            .with_showtime(
                MovieShowtimeMother()
                .with_id(Id("f48c4dae-b0e2-43f6-a659-599f5e254270"))
                .with_show_datetime(DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)))
                .create()
            )
            .build(),
        ]

    def test_find_movies_by_showtime_date(
        self, mock_movie_finder: Mock, movies: list[Movie], showtime_date: Date
    ) -> None:
        mock_movie_finder.find_movies_by_showtime_date.return_value = movies

        data = FindMovies(finder=mock_movie_finder).execute(
            params=FindMoviesParams(showtime_date=showtime_date, genre_id=None)
        )

        mock_movie_finder.find_movies_by_showtime_date.assert_called_once_with(showtime_date=showtime_date)

        assert data == [
            Movie(
                id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=MovieGenres([Genre(id=Id("d108f84b-3568-446b-896c-3ba2bc74cda8"), name="Comedy")]),
                showtimes=MovieShowtimes(
                    [
                        MovieShowtime(
                            id=Id("b6439a2d-c0c0-45c8-81b7-7d7b155830ba"),
                            show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                        )
                    ]
                ),
            ),
            Movie(
                id=Id("ec725625-f502-4d39-9401-a415d8c1f965"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image="super_mario_bros.jpg",
                genres=MovieGenres(
                    [
                        Genre(
                            id=Id("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                            name="Adventure",
                        )
                    ]
                ),
                showtimes=MovieShowtimes(
                    [
                        MovieShowtime(
                            id=Id("f48c4dae-b0e2-43f6-a659-599f5e254270"),
                            show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                        )
                    ]
                ),
            ),
        ]

    def test_find_movies_by_showtime_date_and_genre(
        self, mock_movie_finder: Mock, movies: list[Movie], showtime_date: Date
    ) -> None:
        mock_movie_finder.find_movies_by_showtime_date.return_value = movies

        data = FindMovies(finder=mock_movie_finder).execute(
            params=FindMoviesParams(showtime_date=showtime_date, genre_id=Id("d108f84b-3568-446b-896c-3ba2bc74cda9"))
        )

        mock_movie_finder.find_movies_by_showtime_date.assert_called_once_with(showtime_date=showtime_date)

        assert data == [
            Movie(
                id=Id("ec725625-f502-4d39-9401-a415d8c1f965"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image="super_mario_bros.jpg",
                genres=MovieGenres([Genre(id=Id("d108f84b-3568-446b-896c-3ba2bc74cda9"), name="Adventure")]),
                showtimes=MovieShowtimes(
                    [
                        MovieShowtime(
                            id=Id("f48c4dae-b0e2-43f6-a659-599f5e254270"),
                            show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                        )
                    ]
                ),
            ),
        ]

    def test_find_movies_by_showtime_date_and_genre_when_genre_is_not_associated_to_any_movie(
        self, mock_movie_finder: Mock, movies: list[Movie], showtime_date: Date
    ) -> None:
        mock_movie_finder.find_movies_by_showtime_date.return_value = movies

        data = FindMovies(finder=mock_movie_finder).execute(
            params=FindMoviesParams(showtime_date=showtime_date, genre_id=Id("b108f84b-3568-446b-896c-3ba2bc74cda9"))
        )

        mock_movie_finder.find_movies_by_showtime_date.assert_called_once_with(showtime_date=showtime_date)

        assert data == []
