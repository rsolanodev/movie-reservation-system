from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.movies.application.update_movie import UpdateMovie, UpdateMovieParams
from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.movie import Movie
from app.movies.domain.poster_image import PosterImage
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestUpdateMovie:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    @pytest.fixture
    def movie(self) -> Movie:
        return (
            MovieBuilder()
            .with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_title(title="Deadpool & Wolverine")
            .with_description(description="Deadpool and a variant of Wolverine.")
            .with_poster_image(poster_image="deadpool_and_wolverine.jpg")
            .build()
        )

    @pytest.fixture
    def poster_image(self) -> PosterImage:
        return PosterImage(
            filename="super_mario_bros.jpg",
            content=b"image",
            content_type="image/jpeg",
        )

    def test_updates_movie(self, mock_repository: Mock, movie: Movie, poster_image: PosterImage) -> None:
        mock_repository.get.return_value = movie

        movie = UpdateMovie(repository=mock_repository).execute(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image=poster_image,
            )
        )

        mock_repository.get.assert_called_once_with(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
        mock_repository.save.assert_called_once_with(movie=movie)

        assert movie.title == "The Super Mario Bros. Movie"
        assert movie.description == "An animated adaptation of the video game."
        assert movie.poster_image == "super_mario_bros.jpg"

    def test_does_not_update_movie_when_params_are_none(self, mock_repository: Mock, movie: Movie) -> None:
        mock_repository.get.return_value = movie

        movie = UpdateMovie(repository=mock_repository).execute(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title=None,
                description=None,
                poster_image=None,
            )
        )

        mock_repository.get.assert_called_once_with(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
        mock_repository.save.assert_called_once_with(movie=movie)

        assert movie.title == "Deadpool & Wolverine"
        assert movie.description == "Deadpool and a variant of Wolverine."
        assert movie.poster_image == "deadpool_and_wolverine.jpg"

    def test_raise_exception_when_movie_does_not_exist(self, mock_repository: Mock, poster_image: PosterImage) -> None:
        mock_repository.get.return_value = None

        with pytest.raises(MovieDoesNotExist):
            UpdateMovie(repository=mock_repository).execute(
                params=UpdateMovieParams(
                    id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                    title="The Super Mario Bros. Movie",
                    description="An animated adaptation of the video game.",
                    poster_image=poster_image,
                )
            )

        mock_repository.get.assert_called_once_with(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
        mock_repository.save.assert_not_called()
