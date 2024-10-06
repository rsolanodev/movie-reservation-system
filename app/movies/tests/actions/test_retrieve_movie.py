from datetime import datetime
from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.movies.actions.retrieve_movie import RetrieveMovie
from app.movies.domain.entities import Genre, Movie, MovieShowtime
from app.movies.domain.exceptions import MovieDoesNotExistException
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.domain.factories.genre_factory import GenreFactory
from app.movies.tests.domain.factories.movie_showtime_factory import (
    MovieShowtimeFactory,
)
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestRetrieveMovie:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_retrieves_movie(self, mock_repository: Mock) -> None:
        mock_repository.get.return_value = (
            MovieBuilder()
            .with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_title("The Super Mario Bros. Movie")
            .with_description("An animated adaptation of the video game.")
            .with_poster_image("super_mario_bros.jpg")
            .with_genre(
                genre=GenreFactory().create(
                    id=UUID("c8693e5a-ac9c-4560-9970-7ae4f22ddf0a"),
                    name="Adventure",
                )
            )
            .build()
        )
        mock_repository.get_showtimes.return_value = [
            MovieShowtimeFactory().create(
                id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                show_datetime=datetime(2023, 4, 3, 22, 0),
            )
        ]

        movie = RetrieveMovie(repository=mock_repository).execute(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )

        mock_repository.get.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
        mock_repository.get_showtimes.assert_called_once_with(
            movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
        assert movie == Movie(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            title="The Super Mario Bros. Movie",
            description="An animated adaptation of the video game.",
            poster_image="super_mario_bros.jpg",
            genres=[
                Genre(
                    id=UUID("c8693e5a-ac9c-4560-9970-7ae4f22ddf0a"),
                    name="Adventure",
                )
            ],
            showtimes=[
                MovieShowtime(
                    id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                    show_datetime=datetime(2023, 4, 3, 22, 0),
                )
            ],
        )

    def test_raise_exception_when_movie_does_not_exist(
        self, mock_repository: Mock
    ) -> None:
        mock_repository.get.return_value = None

        with pytest.raises(MovieDoesNotExistException):
            RetrieveMovie(repository=mock_repository).execute(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
            )

        mock_repository.get.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
