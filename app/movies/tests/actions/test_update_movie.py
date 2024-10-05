from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.core.domain.constants.unset import UNSET
from app.movies.actions.update_movie import UpdateMovie, UpdateMovieParams
from app.movies.domain.entities import PosterImage
from app.movies.domain.exceptions import MovieDoesNotExistException
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestUpdateMovie:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_updates_movie(self, mock_repository: Mock) -> None:
        mock_repository.get.return_value = (
            MovieBuilder()
            .with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .build()
        )

        movie = UpdateMovie(repository=mock_repository).execute(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image=None,
            )
        )

        mock_repository.get.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
        mock_repository.save.assert_called_once_with(movie=movie)

        assert movie.title == "The Super Mario Bros. Movie"
        assert movie.description == "An animated adaptation of the video game."
        assert movie.poster_image is None

    def test_raise_exception_when_movie_does_not_exist(
        self, mock_repository: Mock
    ) -> None:
        mock_repository.get.return_value = None

        with pytest.raises(MovieDoesNotExistException):
            poster_image = PosterImage(
                filename="super_mario_bros.jpg",
                content=b"image",
                content_type="image/jpeg",
            )
            UpdateMovie(repository=mock_repository).execute(
                params=UpdateMovieParams(
                    id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                    title="The Super Mario Bros. Movie",
                    description="An animated adaptation of the video game.",
                    poster_image=poster_image,
                )
            )

        mock_repository.get.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
        mock_repository.save.assert_not_called()

    def test_does_not_update_title_when_is_not_sent(
        self, mock_repository: Mock
    ) -> None:
        mock_repository.get.return_value = (
            MovieBuilder()
            .with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .build()
        )

        movie = UpdateMovie(repository=mock_repository).execute(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title=UNSET,
                description="An animated adaptation of the video game.",
                poster_image=None,
            )
        )

        mock_repository.get.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
        mock_repository.save.assert_called_once_with(movie=movie)

        assert movie.title == "Deadpool & Wolverine"
        assert movie.description == "An animated adaptation of the video game."
        assert movie.poster_image is None

    def test_does_not_update_description_when_is_not_sent(
        self, mock_repository: Mock
    ) -> None:
        mock_repository.get.return_value = (
            MovieBuilder()
            .with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .build()
        )

        movie = UpdateMovie(repository=mock_repository).execute(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title="The Super Mario Bros. Movie",
                description=UNSET,
                poster_image=None,
            )
        )

        mock_repository.get.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
        mock_repository.save.assert_called_once_with(movie=movie)

        assert movie.title == "The Super Mario Bros. Movie"
        assert movie.description == "Deadpool and a variant of Wolverine."
        assert movie.poster_image is None

    def test_does_not_update_poster_image_when_is_not_sent(
        self, mock_repository: Mock
    ) -> None:
        mock_repository.get.return_value = (
            MovieBuilder()
            .with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .build()
        )

        movie = UpdateMovie(repository=mock_repository).execute(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image=UNSET,
            )
        )

        mock_repository.get.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )
        mock_repository.save.assert_called_once_with(movie=movie)

        assert movie.title == "The Super Mario Bros. Movie"
        assert movie.description == "An animated adaptation of the video game."
        assert movie.poster_image == "deadpool_and_wolverine.jpg"
