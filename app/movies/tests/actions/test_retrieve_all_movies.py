from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock, call, create_autospec
from uuid import UUID

import pytest
from freezegun import freeze_time

from app.movies.actions.retrieve_all_movies import RetrieveAllMovies
from app.movies.domain.entities import Genre, Movie, MovieShowtime
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.domain.factories.genre_factory import GenreFactory
from app.movies.tests.domain.factories.movie_showtime_factory import (
    MovieShowtimeFactory,
)
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


@freeze_time("2023-04-03T22:00:00Z")
class TestRetrieveAllMovies:
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
            .with_genre(
                genre=GenreFactory().create(
                    id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda8"), name="Comedy"
                )
            )
            .build(),
            MovieBuilder()
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"))
            .with_title("The Super Mario Bros. Movie")
            .with_description("An animated adaptation of the video game.")
            .with_poster_image("super_mario_bros.jpg")
            .with_genre(
                genre=GenreFactory().create(
                    id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"), name="Adventure"
                )
            )
            .build(),
        ]

    def test_retrieves_all_movies(
        self, mock_repository: Mock, movies: list[Movie]
    ) -> None:
        mock_repository.get_all.return_value = movies
        mock_repository.get_showtimes.return_value = []

        all_movies = RetrieveAllMovies(repository=mock_repository).execute()

        mock_repository.get_all.assert_called_once()
        mock_repository.get_showtimes.assert_has_calls(
            [
                call(movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")),
                call(movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f965")),
            ],
            any_order=True,
        )

        assert all_movies == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=[
                    Genre(
                        id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda8"), name="Comedy"
                    )
                ],
                showtimes=[],
            ),
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image="super_mario_bros.jpg",
                genres=[
                    Genre(
                        id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                        name="Adventure",
                    )
                ],
                showtimes=[],
            ),
        ]

    def test_retrieves_all_movies_with_showtimes(
        self, mock_repository: Mock, movies: list[Movie]
    ) -> None:
        mock_repository.get_all.return_value = movies
        mock_repository.get_showtimes.side_effect = [
            [
                MovieShowtimeFactory().create(
                    id=UUID("b6439a2d-c0c0-45c8-81b7-7d7b155830ba"),
                    show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                ),
                MovieShowtimeFactory().create(
                    id=UUID("e5c4f85b-bf9f-4316-b652-1f82890d7915"),
                    show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
                ),
            ],
            [
                MovieShowtimeFactory().create(
                    id=UUID("f48c4dae-b0e2-43f6-a659-599f5e254270"),
                    show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                ),
            ],
        ]

        all_movies = RetrieveAllMovies(repository=mock_repository).execute()

        mock_repository.get_all.assert_called_once()
        mock_repository.get_showtimes.assert_has_calls(
            [
                call(movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")),
                call(movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f965")),
            ],
            any_order=True,
        )

        assert all_movies == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=[
                    Genre(
                        id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda8"), name="Comedy"
                    )
                ],
                showtimes=[
                    MovieShowtime(
                        id=UUID("b6439a2d-c0c0-45c8-81b7-7d7b155830ba"),
                        show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                    ),
                    MovieShowtime(
                        id=UUID("e5c4f85b-bf9f-4316-b652-1f82890d7915"),
                        show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
                    ),
                ],
            ),
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image="super_mario_bros.jpg",
                genres=[
                    Genre(
                        id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                        name="Adventure",
                    )
                ],
                showtimes=[
                    MovieShowtime(
                        id=UUID("f48c4dae-b0e2-43f6-a659-599f5e254270"),
                        show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                    ),
                ],
            ),
        ]

    def test_does_not_retrieve_old_showtimes(
        self, mock_repository: Mock, movies: list[Movie]
    ) -> None:
        mock_repository.get_all.return_value = movies
        mock_repository.get_showtimes.side_effect = [
            [
                MovieShowtimeFactory().create(
                    id=UUID("b6439a2d-c0c0-45c8-81b7-7d7b155830ba"),
                    show_datetime=datetime(2023, 4, 3, 21, 0, tzinfo=timezone.utc),
                ),
                MovieShowtimeFactory().create(
                    id=UUID("e5c4f85b-bf9f-4316-b652-1f82890d7915"),
                    show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
                ),
            ],
            [
                MovieShowtimeFactory().create(
                    id=UUID("f48c4dae-b0e2-43f6-a659-599f5e254270"),
                    show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                ),
            ],
        ]

        all_movies = RetrieveAllMovies(repository=mock_repository).execute()

        mock_repository.get_all.assert_called_once()
        mock_repository.get_showtimes.assert_has_calls(
            [
                call(movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")),
                call(movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f965")),
            ],
            any_order=True,
        )

        assert all_movies == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=[
                    Genre(
                        id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda8"), name="Comedy"
                    )
                ],
                showtimes=[
                    MovieShowtime(
                        id=UUID("e5c4f85b-bf9f-4316-b652-1f82890d7915"),
                        show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
                    ),
                ],
            ),
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image="super_mario_bros.jpg",
                genres=[
                    Genre(
                        id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                        name="Adventure",
                    )
                ],
                showtimes=[
                    MovieShowtime(
                        id=UUID("f48c4dae-b0e2-43f6-a659-599f5e254270"),
                        show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                    ),
                ],
            ),
        ]

    def test_retrieves_movies_filtered_by_genre(
        self, mock_repository: Mock, movies: list[Movie]
    ) -> None:
        mock_repository.get_all.return_value = movies
        mock_repository.get_showtimes.return_value = [
            MovieShowtimeFactory().create(
                id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
        ]

        all_movies = RetrieveAllMovies(repository=mock_repository).execute(
            genre_id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9")
        )

        mock_repository.get_all.assert_called_once()
        mock_repository.get_showtimes.assert_has_calls(
            [
                call(movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f965")),
            ],
            any_order=True,
        )

        assert all_movies == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image="super_mario_bros.jpg",
                genres=[
                    Genre(
                        id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                        name="Adventure",
                    )
                ],
                showtimes=[
                    MovieShowtime(
                        id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                        show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                    )
                ],
            ),
        ]

    def test_retrieves_movies_filtered_by_genre_that_does_not_exist(
        self, mock_repository: Mock, movies: list[Movie]
    ) -> None:
        mock_repository.get_all.return_value = movies

        all_movies = RetrieveAllMovies(repository=mock_repository).execute(
            genre_id=UUID("b108f84b-3568-446b-896c-3ba2bc74cda9")
        )

        mock_repository.get_all.assert_called_once()
        mock_repository.get_showtimes.assert_not_called()

        assert all_movies == []
