from io import BytesIO
from typing import Any
from unittest.mock import Mock, create_autospec

import pytest
from fastapi import UploadFile
from fastapi_storages.base import BaseStorage

from app.movies.application.create_movie import CreateMovie, CreateMovieParams
from app.movies.domain.poster_image import PosterImage
from app.movies.domain.repositories.movie_repository import MovieRepository


class TestCreateMovie:
    @pytest.fixture
    def mock_movie_repository(self) -> Any:
        return create_autospec(spec=MovieRepository, instance=True, spec_set=True)

    @pytest.fixture
    def mock_storage(self) -> Any:
        return create_autospec(spec=BaseStorage, instance=True, spec_set=True)

    def test_creates_movie(self, mock_movie_repository: Mock, mock_storage: Mock) -> None:
        mock_storage.write.return_value = "poster_image.jpg"

        file = BytesIO(b"image content")
        poster_image = UploadFile(file=file, filename="poster_image.jpg")

        movie = CreateMovie(repository=mock_movie_repository, storage=mock_storage).execute(
            params=CreateMovieParams(
                title="Deadpool & Wolverine",
                description=(
                    "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
                    "Variance Authority, but instead recruits a variant of Wolverine to save "
                    "his universe from extinction."
                ),
                poster_image=PosterImage(filename=poster_image.filename, file=file),
            )
        )

        mock_movie_repository.save.assert_called_once_with(movie=movie)

        assert movie.title == "Deadpool & Wolverine"
        assert movie.description == (
            "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
            "Variance Authority, but instead recruits a variant of Wolverine to save "
            "his universe from extinction."
        )
        assert movie.poster_image == "poster_image.jpg"

    def test_creates_movie_without_poster_image(self, mock_movie_repository: Mock, mock_storage: Mock) -> None:
        movie = CreateMovie(repository=mock_movie_repository, storage=mock_storage).execute(
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

        mock_movie_repository.save.assert_called_once_with(movie=movie)
        mock_storage.write.assert_not_called()

        assert movie.title == "Deadpool & Wolverine"
        assert movie.description == (
            "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
            "Variance Authority, but instead recruits a variant of Wolverine to save "
            "his universe from extinction."
        )
        assert movie.poster_image is None
