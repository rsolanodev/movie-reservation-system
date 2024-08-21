from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.movies.actions.create_movie import CreateMovieParams
from app.movies.domain.entities import PosterImage
from app.movies.tests.factories.movie_factory import MovieFactory


class TestCreateMovieEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.CreateMovie") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch(
            "app.movies.infrastructure.api.endpoints.SqlModelMovieRepository"
        ) as mock:
            yield mock.return_value

    def test_returns_201_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        mock_action.return_value.execute.return_value = MovieFactory().create()
        response = client.post(
            "api/v1/movies/",
            data={
                "title": "Deadpool & Wolverine",
                "description": (
                    "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
                    "Variance Authority, but instead recruits a variant of Wolverine to save "
                    "his universe from extinction."
                ),
            },
            files={"poster_image": ("deadpool_and_wolverine.jpg", b"image")},
        )
        assert response.status_code == 201
        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=CreateMovieParams(
                title="Deadpool & Wolverine",
                description=(
                    "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
                    "Variance Authority, but instead recruits a variant of Wolverine to save "
                    "his universe from extinction."
                ),
                poster_image=PosterImage(
                    filename="deadpool_and_wolverine.jpg",
                    content=b"image",
                    content_type="image/jpeg",
                ),
            )
        )
        assert response.status_code == 201
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "title": "Deadpool & Wolverine",
            "description": (
                "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
                "Variance Authority, but instead recruits a variant of Wolverine to save "
                "his universe from extinction."
            ),
            "poster_image": "deadpool_and_wolverine.jpg",
        }

    def test_returns_201_and_calls_action_when_does_not_have_poster_image(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        mock_action.return_value.execute.return_value = MovieFactory().create(
            poster_image=None
        )
        response = client.post(
            "api/v1/movies/",
            data={
                "title": "Deadpool & Wolverine",
                "description": (
                    "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
                    "Variance Authority, but instead recruits a variant of Wolverine to save "
                    "his universe from extinction."
                ),
            },
        )
        assert response.status_code == 201
        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
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
        assert response.status_code == 201
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "title": "Deadpool & Wolverine",
            "description": (
                "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
                "Variance Authority, but instead recruits a variant of Wolverine to save "
                "his universe from extinction."
            ),
            "poster_image": None,
        }
