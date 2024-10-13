from collections.abc import Generator
from datetime import date, datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.movies.application.create_movie import CreateMovieParams
from app.movies.application.retrieve_movie import RetrieveMovieParams
from app.movies.application.retrieve_movies import RetrieveMoviesParams
from app.movies.application.update_movie import UpdateMovieParams
from app.movies.domain.exceptions import (
    GenreAlreadyAssigned,
    GenreNotAssigned,
    MovieDoesNotExist,
)
from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.domain.poster_image import PosterImage
from app.movies.tests.domain.factories.genre_factory import GenreFactory
from app.movies.tests.domain.factories.movie_showtime_factory import (
    MovieShowtimeFactory,
)
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestCreateMovieEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.CreateMovie") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

    def test_returns_201_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.return_value = (
            MovieBuilder().with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")).build()
        )

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
        mock_action.return_value.execute.return_value = (
            MovieBuilder().with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")).without_poster_image().build()
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
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

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

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
        movie: Movie,
    ) -> None:
        mock_action.return_value.execute.return_value = movie

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
        movie: Movie,
    ) -> None:
        mock_action.return_value.execute.return_value = movie

        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=UpdateMovieParams(
                id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title=None,
                description=None,
                poster_image=None,
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
        mock_action.return_value.execute.side_effect = MovieDoesNotExist

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
                poster_image=None,
            )
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "The movie does not exist"}

    def test_returns_401_when_user_is_not_authenticated(
        self, client: TestClient, mock_action: Mock, mock_repository: Mock
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
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
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
        mock_action.return_value.execute.assert_called_once_with(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))

        assert response.status_code == 200

    def test_returns_404_when_movie_does_not_exist(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.side_effect = MovieDoesNotExist

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


class TestRetrieveGenresEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.RetrieveGenres") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelGenreRepository") as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        action_genre = Genre.create(name="Action")
        adventure_genre = Genre.create(name="Adventure")
        comedy_genre = Genre.create(name="Comedy")

        mock_action.return_value.execute.return_value = [
            action_genre,
            adventure_genre,
            comedy_genre,
        ]

        response = client.get("api/v1/movies/genres/")

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once()

        assert response.status_code == 200
        assert response.json() == [
            {"id": str(action_genre.id), "name": "Action"},
            {"id": str(adventure_genre.id), "name": "Adventure"},
            {"id": str(comedy_genre.id), "name": "Comedy"},
        ]


class TestAddMovieGenreEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.AddMovieGenre") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.return_value = None

        response = client.post(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/genres/",
            data={"genre_id": "2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"},
            headers=superuser_token_headers,
        )
        assert response.status_code == 200

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            genre_id=UUID("2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"),
        )

        assert response.status_code == 200

    def test_returns_400_and_calls_action_when_genre_already_assigned(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.side_effect = GenreAlreadyAssigned

        response = client.post(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/genres/",
            data={"genre_id": "2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"},
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            genre_id=UUID("2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"),
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "The genre is already assigned to the movie"}


class TestRemoveMovieGenreEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.RemoveMovieGenre") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
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
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/genres/2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e/",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            genre_id=UUID("2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"),
        )

        assert response.status_code == 200

    def test_returns_400_and_calls_action_when_genre_not_assigned(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.side_effect = GenreNotAssigned

        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/genres/2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e/",
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            genre_id=UUID("2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"),
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "The genre is not assigned to the movie"}


class TestRetrieveMovieEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.RetrieveMovie") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        mock_action.return_value.execute.return_value = (
            MovieBuilder()
            .with_id(id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_genre(
                genre=GenreFactory().create(
                    id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                    name="Action",
                )
            )
            .with_genre(
                genre=GenreFactory().create(
                    id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda8"),
                    name="Comedy",
                )
            )
            .with_showtime(
                showtime=MovieShowtimeFactory().create(
                    id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                    show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                )
            )
            .build()
        )

        response = client.get("api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/?showtime_date=2023-04-03")

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=RetrieveMovieParams(
                movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                showtime_date=date(2023, 4, 3),
            )
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "title": "Deadpool & Wolverine",
            "description": "Deadpool and a variant of Wolverine.",
            "poster_image": "deadpool_and_wolverine.jpg",
            "genres": [
                {"id": "d108f84b-3568-446b-896c-3ba2bc74cda9", "name": "Action"},
                {"id": "d108f84b-3568-446b-896c-3ba2bc74cda8", "name": "Comedy"},
            ],
            "showtimes": [
                {
                    "id": "d7c10c00-9598-4618-956a-ff3aa82dd33f",
                    "show_datetime": "2023-04-03T22:00:00Z",
                }
            ],
        }

    def test_returns_404_when_movie_does_not_exist(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        mock_action.return_value.execute.side_effect = MovieDoesNotExist

        response = client.get("api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/?showtime_date=2023-04-03")

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=RetrieveMovieParams(
                movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                showtime_date=date(2023, 4, 3),
            )
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "The movie does not exist"}


class TestRetrieveMoviesEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.RetrieveMovies") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(self, client: TestClient, mock_action: Mock, mock_repository: Mock) -> None:
        mock_action.return_value.execute.return_value = [
            MovieBuilder()
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_title("Deadpool & Wolverine")
            .with_description("Deadpool and a variant of Wolverine.")
            .with_poster_image("deadpool_and_wolverine.jpg")
            .with_genre(genre=GenreFactory().create(id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda8"), name="Comedy"))
            .with_showtime(
                showtime=MovieShowtimeFactory().create(
                    id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
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
                showtime=MovieShowtimeFactory().create(
                    id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd44f"),
                    show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
                )
            )
            .build(),
        ]

        response = client.get("api/v1/movies/?available_date=2023-04-03")

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=RetrieveMoviesParams(available_date=date(2023, 4, 3), genre_id=None)
        )

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "ec725625-f502-4d39-9401-a415d8c1f964",
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
                "poster_image": "deadpool_and_wolverine.jpg",
                "genres": [{"id": "d108f84b-3568-446b-896c-3ba2bc74cda8", "name": "Comedy"}],
                "showtimes": [
                    {
                        "id": "d7c10c00-9598-4618-956a-ff3aa82dd33f",
                        "show_datetime": "2023-04-03T22:00:00Z",
                    }
                ],
            },
            {
                "id": "ec725625-f502-4d39-9401-a415d8c1f965",
                "title": "The Super Mario Bros. Movie",
                "description": "An animated adaptation of the video game.",
                "poster_image": "super_mario_bros.jpg",
                "genres": [{"id": "d108f84b-3568-446b-896c-3ba2bc74cda9", "name": "Adventure"}],
                "showtimes": [
                    {
                        "id": "d7c10c00-9598-4618-956a-ff3aa82dd44f",
                        "show_datetime": "2023-04-03T23:00:00Z",
                    }
                ],
            },
        ]

    def test_returns_200_and_calls_action_with_genre_filter(
        self, client: TestClient, mock_action: Mock, mock_repository: Mock
    ) -> None:
        mock_action.return_value.execute.return_value = [
            MovieBuilder()
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_genre(genre=GenreFactory().create(id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"), name="Action"))
            .with_showtime(
                showtime=MovieShowtimeFactory().create(
                    id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                    show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                )
            )
            .build()
        ]

        response = client.get("api/v1/movies/?available_date=2023-04-03&genre_id=d108f84b-3568-446b-896c-3ba2bc74cda9")

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=RetrieveMoviesParams(
                available_date=date(2023, 4, 3),
                genre_id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
            )
        )

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "ec725625-f502-4d39-9401-a415d8c1f964",
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
                "poster_image": "deadpool_and_wolverine.jpg",
                "genres": [{"id": "d108f84b-3568-446b-896c-3ba2bc74cda9", "name": "Action"}],
                "showtimes": [
                    {
                        "id": "d7c10c00-9598-4618-956a-ff3aa82dd33f",
                        "show_datetime": "2023-04-03T22:00:00Z",
                    }
                ],
            }
        ]

    def test_returns_empty_list_when_no_movies(
        self, client: TestClient, mock_action: Mock, mock_repository: Mock
    ) -> None:
        mock_action.return_value.execute.return_value = []

        response = client.get("api/v1/movies/?available_date=2023-04-03")

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=RetrieveMoviesParams(available_date=date(2023, 4, 3), genre_id=None)
        )

        assert response.status_code == 200
        assert response.json() == []
