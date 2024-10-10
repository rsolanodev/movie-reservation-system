from datetime import date, datetime, timezone
from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest
from freezegun import freeze_time

from app.movies.application.retrieve_movies import RetrieveMovies, RetrieveMoviesParams
from app.movies.domain.collections.movie_genres import MovieGenres
from app.movies.domain.collections.movie_showtimes import MovieShowtimes
from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.domain.movie_showtime import MovieShowtime
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.domain.factories.genre_factory import GenreFactory
from app.movies.tests.domain.factories.movie_showtime_factory import MovieShowtimeFactory
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


@freeze_time("2023-04-03T22:00:00Z")
class TestRetrieveMovies:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    @pytest.fixture
    def movies(self) -> list[Movie]:
        return [
            MovieBuilder()
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_title("Deadpool & Wolverine")
            .with_description("Deadpool and a variant of Wolverine.")
            .with_poster_image("deadpool_and_wolverine.jpg")
            .with_genre(genre=GenreFactory().create(id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda8"), name="Comedy"))
            .with_showtime(
                MovieShowtimeFactory().create(
                    id=UUID("b6439a2d-c0c0-45c8-81b7-7d7b155830ba"),
                    show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                )
            )
            .build(),
            MovieBuilder()
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"))
            .with_title("The Super Mario Bros. Movie")
            .with_description("An animated adaptation of the video game.")
            .with_poster_image("super_mario_bros.jpg")
            .with_genre(genre=GenreFactory().create(id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"), name="Adventure"))
            .with_showtime(
                MovieShowtimeFactory().create(
                    id=UUID("f48c4dae-b0e2-43f6-a659-599f5e254270"),
                    show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                )
            )
            .build(),
        ]

    def test_retrieves_available_movies_for_date(self, mock_repository: Mock, movies: list[Movie]) -> None:
        mock_repository.get_available_movies_for_date.return_value = movies

        data = RetrieveMovies(repository=mock_repository).execute(
            params=RetrieveMoviesParams(available_date=date(2023, 4, 3))
        )

        mock_repository.get_available_movies_for_date.assert_called_once_with(available_date=date(2023, 4, 3))

        assert data == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=MovieGenres([Genre(id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda8"), name="Comedy")]),
                showtimes=MovieShowtimes(
                    [
                        MovieShowtime(
                            id=UUID("b6439a2d-c0c0-45c8-81b7-7d7b155830ba"),
                            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                        )
                    ]
                ),
            ),
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image="super_mario_bros.jpg",
                genres=MovieGenres(
                    [
                        Genre(
                            id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                            name="Adventure",
                        )
                    ]
                ),
                showtimes=MovieShowtimes(
                    [
                        MovieShowtime(
                            id=UUID("f48c4dae-b0e2-43f6-a659-599f5e254270"),
                            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                        )
                    ]
                ),
            ),
        ]

    def test_retrieves_available_movies_for_date_filtered_by_genre(
        self, mock_repository: Mock, movies: list[Movie]
    ) -> None:
        mock_repository.get_available_movies_for_date.return_value = movies

        data = RetrieveMovies(repository=mock_repository).execute(
            params=RetrieveMoviesParams(
                available_date=date(2023, 4, 3),
                genre_id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
            )
        )

        mock_repository.get_available_movies_for_date.assert_called_once_with(available_date=date(2023, 4, 3))

        assert data == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image="super_mario_bros.jpg",
                genres=MovieGenres([Genre(id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"), name="Adventure")]),
                showtimes=MovieShowtimes(
                    [
                        MovieShowtime(
                            id=UUID("f48c4dae-b0e2-43f6-a659-599f5e254270"),
                            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                        )
                    ]
                ),
            ),
        ]

    def test_retrieves_available_movies_for_date_filtered_by_genre_that_does_not_exist(
        self, mock_repository: Mock, movies: list[Movie]
    ) -> None:
        mock_repository.get_available_movies_for_date.return_value = movies

        data = RetrieveMovies(repository=mock_repository).execute(
            params=RetrieveMoviesParams(
                available_date=date(2023, 4, 3),
                genre_id=UUID("b108f84b-3568-446b-896c-3ba2bc74cda9"),
            )
        )

        mock_repository.get_available_movies_for_date.assert_called_once_with(available_date=date(2023, 4, 3))

        assert data == []
