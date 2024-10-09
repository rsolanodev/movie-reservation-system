import tempfile
from typing import Any
from unittest.mock import Mock, create_autospec

import pytest
from fastapi import UploadFile

from app.movies.application.create_movie import CreateMovie, CreateMovieParams
from app.movies.domain.entities import PosterImage
from app.movies.domain.repositories.movie_repository import MovieRepository


class TestCreateMovie:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_creates_movie(self, mock_repository: Mock) -> None:
        poster_image = UploadFile(
            file=tempfile.NamedTemporaryFile(),  # type: ignore
            filename="poster_image.jpg",
        )
        movie = CreateMovie(repository=mock_repository).execute(
            params=CreateMovieParams(
                title="Deadpool & Wolverine",
                description=(
                    "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
                    "Variance Authority, but instead recruits a variant of Wolverine to save "
                    "his universe from extinction."
                ),
                poster_image=PosterImage(
                    filename=poster_image.filename,
                    content=poster_image.file.read(),
                    content_type=poster_image.content_type,
                ),
            )
        )

        mock_repository.save.assert_called_once_with(movie=movie)

        assert movie.title == "Deadpool & Wolverine"
        assert movie.description == (
            "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
            "Variance Authority, but instead recruits a variant of Wolverine to save "
            "his universe from extinction."
        )
        assert movie.poster_image == "poster_image.jpg"

    def test_creates_movie_without_poster_image(self, mock_repository: Mock) -> None:
        movie = CreateMovie(repository=mock_repository).execute(
            params=CreateMovieParams(
                title="Deadpool & Wolverine",
                description=(
                    "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
                    "Variance Authority, but instead recruits a variant of Wolverine to save "
                    "his universe from extinction."
                ),
                poster_image=None,
            )
        )

        mock_repository.save.assert_called_once_with(movie=movie)

        assert movie.title == "Deadpool & Wolverine"
        assert movie.description == (
            "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
            "Variance Authority, but instead recruits a variant of Wolverine to save "
            "his universe from extinction."
        )
        assert movie.poster_image is None
