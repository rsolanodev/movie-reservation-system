from collections.abc import Generator
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.core.domain.constants.unset import UNSET
from app.movies.actions.create_movie import CreateMovieParams
from app.movies.actions.update_movie import UpdateMovieParams
from app.movies.domain.entities import Category, PosterImage
from app.movies.domain.exceptions import MovieDoesNotExistException
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
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.return_value = MovieFactory().create()

        response = client.post(
            "api/v1/movies/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            files={"poster_image": ("deadpool_and_wolverine.jpg", b"image")},
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=CreateMovieParams(
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
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
            "description": "Deadpool and a variant of Wolverine.",
            "poster_image": "deadpool_and_wolverine.jpg",
        }

    def test_returns_201_and_calls_action_when_does_not_have_poster_image(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.return_value = MovieFactory().create(
            poster_image=None
        )

        response = client.post(
            "api/v1/movies/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=CreateMovieParams(
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image=None,
            )
        )

        assert response.status_code == 201
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "title": "Deadpool & Wolverine",
            "description": "Deadpool and a variant of Wolverine.",
            "poster_image": None,
        }

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        response = client.post(
            "api/v1/movies/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "api/v1/movies/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            headers=user_token_headers,
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestUpdateMovieEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.UpdateMovie") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch(
            "app.movies.infrastructure.api.endpoints.SqlModelMovieRepository"
        ) as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.return_value = MovieFactory().create()

        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            files={"poster_image": ("deadpool_and_wolverine.jpg", b"image")},
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image=PosterImage(
                    filename="deadpool_and_wolverine.jpg",
                    content=b"image",
                    content_type="image/jpeg",
                ),
            )
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "title": "Deadpool & Wolverine",
            "description": "Deadpool and a variant of Wolverine.",
            "poster_image": "deadpool_and_wolverine.jpg",
        }

    def test_returns_200_and_calls_action_when_data_is_not_sent(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.return_value = MovieFactory().create()

        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title=UNSET,
                description=UNSET,
                poster_image=UNSET,
            )
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "title": "Deadpool & Wolverine",
            "description": "Deadpool and a variant of Wolverine.",
            "poster_image": "deadpool_and_wolverine.jpg",
        }

    def test_returns_404_when_movie_does_not_exist(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.side_effect = MovieDoesNotExistException()

        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image=UNSET,
            )
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "The movie does not exist"}

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            headers=user_token_headers,
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestDeleteMovieEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.DeleteMovie") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch(
            "app.movies.infrastructure.api.endpoints.SqlModelMovieRepository"
        ) as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.return_value = None

        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )

        assert response.status_code == 200

    def test_returns_404_when_movie_does_not_exist(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.side_effect = MovieDoesNotExistException()

        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "The movie does not exist"}

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=user_token_headers,
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestRetrieveCategoriesEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch(
            "app.movies.infrastructure.api.endpoints.RetrieveCategories"
        ) as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch(
            "app.movies.infrastructure.api.endpoints.SqlModelCategoryRepository"
        ) as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        action_category = Category.create(name="Action")
        adventure_category = Category.create(name="Adventure")
        comedy_category = Category.create(name="Comedy")

        mock_action.return_value.execute.return_value = [
            action_category,
            adventure_category,
            comedy_category,
        ]

        response = client.get("api/v1/movies/categories/")

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once()

        assert response.status_code == 200
        assert response.json() == [
            {"id": str(action_category.id), "name": "Action"},
            {"id": str(adventure_category.id), "name": "Adventure"},
            {"id": str(comedy_category.id), "name": "Comedy"},
        ]
