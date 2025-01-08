from collections.abc import Generator
from datetime import date, datetime, timezone
from unittest.mock import ANY, Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.movies.application.commands.add_movie_genre import AddMovieGenreParams
from app.movies.application.commands.create_movie import CreateMovieParams
from app.movies.application.commands.update_movie import UpdateMovieParams
from app.movies.application.queries.find_movie import FindMovieParams
from app.movies.application.queries.find_movies import FindMoviesParams
from app.movies.domain.exceptions import (
    GenreAlreadyAssigned,
    GenreNotAssigned,
    MovieDoesNotExist,
)
from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.domain.poster_image import PosterImage
from app.movies.infrastructure.models import MovieModel
from app.movies.tests.factories.genre_factory_test import GenreFactoryTest
from app.movies.tests.factories.movie_showtime_factory_test import (
    MovieShowtimeFactoryTest,
)
from app.movies.tests.factories.sqlmodel_genre_factory_test import SqlModelGenreFactoryTest
from app.shared.domain.value_objects.date import Date
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.tests.builders.sqlmodel_movie_builder_test import SqlModelMovieBuilderTest
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestCreateMovieEndpoint:
    @pytest.fixture
    def mock_create_movie(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.CreateMovie") as mock:
            yield mock

    @pytest.fixture
    def mock_movie_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_storage(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.PublicMediaS3Storage") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(
        self, session: Session, client: TestClient, superuser_token_headers: dict[str, str], mock_storage: Mock
    ) -> None:
        mock_storage.write.return_value = "deadpool_and_wolverine.jpg"

        response = client.post(
            "api/v1/movies/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            files={"poster_image": ("deadpool_and_wolverine.jpg", b"image")},
            headers=superuser_token_headers,
        )

        assert response.status_code == 201

        mock_storage.write.assert_called_once_with(file=ANY, name="deadpool_and_wolverine.jpg")

        movie_model = session.exec(select(MovieModel)).first()
        assert movie_model is not None
        assert movie_model.title == "Deadpool & Wolverine"
        assert movie_model.description == "Deadpool and a variant of Wolverine."
        assert movie_model.poster_image == "deadpool_and_wolverine.jpg"

    def test_returns_201_and_calls_create_movie(
        self,
        client: TestClient,
        mock_create_movie: Mock,
        mock_movie_repository: Mock,
        mock_storage: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_create_movie.return_value.execute.return_value = (
            MovieBuilder().with_id(id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d")).build()
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

        mock_create_movie.assert_called_once_with(repository=mock_movie_repository, storage=mock_storage)
        mock_create_movie.return_value.execute.assert_called_once_with(
            params=CreateMovieParams(
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image=PosterImage(filename="deadpool_and_wolverine.jpg", file=ANY),
            )
        )

        assert response.status_code == 201
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "title": "Deadpool & Wolverine",
            "description": "Deadpool and a variant of Wolverine.",
            "poster_image": "deadpool_and_wolverine.jpg",
        }

    def test_returns_201_and_calls_create_movie_when_does_not_have_poster_image(
        self,
        client: TestClient,
        mock_create_movie: Mock,
        mock_movie_repository: Mock,
        mock_storage: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_create_movie.return_value.execute.return_value = (
            MovieBuilder().with_id(id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d")).without_poster_image().build()
        )

        response = client.post(
            "api/v1/movies/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            headers=superuser_token_headers,
        )

        mock_create_movie.assert_called_once_with(repository=mock_movie_repository, storage=mock_storage)
        mock_create_movie.return_value.execute.assert_called_once_with(
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
        mock_create_movie: Mock,
        mock_movie_repository: Mock,
        mock_storage: Mock,
    ) -> None:
        response = client.post(
            "api/v1/movies/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
        )

        mock_create_movie.assert_not_called()
        mock_movie_repository.assert_not_called()
        mock_storage.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_create_movie: Mock,
        mock_movie_repository: Mock,
        mock_storage: Mock,
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

        mock_create_movie.assert_not_called()
        mock_movie_repository.assert_not_called()
        mock_storage.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestUpdateMovieEndpoint:
    @pytest.fixture
    def mock_update_movie(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.UpdateMovie") as mock:
            yield mock

    @pytest.fixture
    def mock_movie_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_movie_finder(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieFinder") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_storage(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.PublicMediaS3Storage") as mock:
            yield mock.return_value

    @pytest.fixture
    def movie(self) -> Movie:
        return (
            MovieBuilder()
            .with_id(id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_title(title="Deadpool & Wolverine")
            .with_description(description="Deadpool and a variant of Wolverine.")
            .with_poster_image(poster_image="deadpool_and_wolverine.jpg")
            .build()
        )

    @pytest.mark.integration
    def test_integration(
        self, session: Session, client: TestClient, mock_storage: Mock, superuser_token_headers: dict[str, str]
    ) -> None:
        mock_storage.write.return_value = "new_poster.jpg"

        movie_model = SqlModelMovieBuilderTest(session=session).build()

        response = client.patch(
            f"api/v1/movies/{movie_model.id}/",
            data={
                "title": "New Title",
                "description": "New description",
            },
            files={"poster_image": ("new_poster.jpg", b"new_image")},
            headers=superuser_token_headers,
        )

        assert response.status_code == 200

        mock_storage.write.assert_called_once_with(file=ANY, name="new_poster.jpg")

        session.refresh(movie_model)
        assert movie_model.title == "New Title"
        assert movie_model.description == "New description"
        assert movie_model.poster_image == "new_poster.jpg"

    def test_returns_200_and_calls_update_movie(
        self,
        client: TestClient,
        mock_update_movie: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        mock_storage: Mock,
        superuser_token_headers: dict[str, str],
        movie: Movie,
    ) -> None:
        mock_update_movie.return_value.execute.return_value = movie

        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            files={"poster_image": ("deadpool_and_wolverine.jpg", b"image")},
            headers=superuser_token_headers,
        )

        mock_update_movie.assert_called_once_with(
            repository=mock_movie_repository, finder=mock_movie_finder, storage=mock_storage
        )
        mock_update_movie.return_value.execute.assert_called_once_with(
            params=UpdateMovieParams(
                id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image=PosterImage(filename="deadpool_and_wolverine.jpg", file=ANY),
            )
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "title": "Deadpool & Wolverine",
            "description": "Deadpool and a variant of Wolverine.",
            "poster_image": "deadpool_and_wolverine.jpg",
        }

    def test_returns_200_and_calls_update_movie_when_data_is_not_sent(
        self,
        client: TestClient,
        mock_update_movie: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        mock_storage: Mock,
        superuser_token_headers: dict[str, str],
        movie: Movie,
    ) -> None:
        mock_update_movie.return_value.execute.return_value = movie

        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_update_movie.assert_called_once_with(
            repository=mock_movie_repository, finder=mock_movie_finder, storage=mock_storage
        )
        mock_update_movie.return_value.execute.assert_called_once_with(
            params=UpdateMovieParams(
                id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
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
        mock_update_movie: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        mock_storage: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_update_movie.return_value.execute.side_effect = MovieDoesNotExist

        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
            headers=superuser_token_headers,
        )

        mock_update_movie.assert_called_once_with(
            repository=mock_movie_repository, finder=mock_movie_finder, storage=mock_storage
        )
        mock_update_movie.return_value.execute.assert_called_once_with(
            params=UpdateMovieParams(
                id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image=None,
            )
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "The movie does not exist"}

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_update_movie: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        mock_storage: Mock,
    ) -> None:
        response = client.patch(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            data={
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
            },
        )

        mock_update_movie.assert_not_called()
        mock_movie_repository.assert_not_called()
        mock_movie_finder.assert_not_called()
        mock_storage.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_update_movie: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        mock_storage: Mock,
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

        mock_update_movie.assert_not_called()
        mock_movie_repository.assert_not_called()
        mock_movie_finder.assert_not_called()
        mock_storage.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestDeleteMovieEndpoint:
    @pytest.fixture
    def mock_delete_movie(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.DeleteMovie") as mock:
            yield mock

    @pytest.fixture
    def mock_movie_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_movie_finder(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, session: Session, client: TestClient, superuser_token_headers: dict[str, str]) -> None:
        movie_model = SqlModelMovieBuilderTest(session=session).build()

        response = client.delete(
            f"api/v1/movies/{movie_model.id}/",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        assert session.get(MovieModel, movie_model.id) is None

    def test_returns_200_and_calls_delete_movie(
        self,
        client: TestClient,
        mock_delete_movie: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_delete_movie.return_value.execute.return_value = None

        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_delete_movie.assert_called_once_with(repository=mock_movie_repository, finder=mock_movie_finder)
        mock_delete_movie.return_value.execute.assert_called_once_with(id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"))

        assert response.status_code == 200

    def test_returns_404_when_movie_does_not_exist(
        self,
        client: TestClient,
        mock_delete_movie: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_delete_movie.return_value.execute.side_effect = MovieDoesNotExist

        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_delete_movie.assert_called_once_with(repository=mock_movie_repository, finder=mock_movie_finder)
        mock_delete_movie.return_value.execute.assert_called_once_with(
            id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "The movie does not exist"}

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_delete_movie: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
    ) -> None:
        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
        )

        mock_delete_movie.assert_not_called()
        mock_movie_repository.assert_not_called()
        mock_movie_finder.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_delete_movie: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=user_token_headers,
        )

        mock_delete_movie.assert_not_called()
        mock_movie_repository.assert_not_called()
        mock_movie_finder.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestListGenresEndpoint:
    @pytest.fixture
    def mock_find_all_genres(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.FindAllGenres") as mock:
            yield mock

    @pytest.fixture
    def mock_genre_finder(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelGenreFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, session: Session, client: TestClient) -> None:
        genre_factory = SqlModelGenreFactoryTest(session=session)
        genre_action = genre_factory.create(name="Action")
        genre_comedy = genre_factory.create(name="Comedy")

        response = client.get("api/v1/movies/genres/")

        assert response.status_code == 200
        assert response.json() == [
            {"id": str(genre_action.id), "name": "Action"},
            {"id": str(genre_comedy.id), "name": "Comedy"},
        ]

    def test_returns_200_and_calls_find_all_genres(
        self,
        client: TestClient,
        mock_find_all_genres: Mock,
        mock_genre_finder: Mock,
    ) -> None:
        action_genre = Genre.create(name="Action")
        adventure_genre = Genre.create(name="Adventure")
        comedy_genre = Genre.create(name="Comedy")

        mock_find_all_genres.return_value.execute.return_value = [
            action_genre,
            adventure_genre,
            comedy_genre,
        ]

        response = client.get("api/v1/movies/genres/")

        mock_find_all_genres.assert_called_once_with(finder=mock_genre_finder)
        mock_find_all_genres.return_value.execute.assert_called_once()

        assert response.status_code == 200
        assert response.json() == [
            {"id": str(action_genre.id), "name": "Action"},
            {"id": str(adventure_genre.id), "name": "Adventure"},
            {"id": str(comedy_genre.id), "name": "Comedy"},
        ]


class TestAddMovieGenreEndpoint:
    @pytest.fixture
    def mock_add_movie_genre(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.AddMovieGenre") as mock:
            yield mock

    @pytest.fixture
    def mock_movie_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_movie_finder(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, session: Session, client: TestClient, superuser_token_headers: dict[str, str]) -> None:
        movie_model = SqlModelMovieBuilderTest(session=session).build()
        genre_model = SqlModelGenreFactoryTest(session=session).create(name="Action")

        response = client.post(
            f"api/v1/movies/{movie_model.id}/genres/",
            data={"genre_id": str(genre_model.id)},
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        assert movie_model.genres[0].id == genre_model.id
        assert movie_model.genres[0].name == "Action"

    def test_returns_200_and_calls_add_movie_genre(
        self,
        client: TestClient,
        mock_add_movie_genre: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_add_movie_genre.return_value.execute.return_value = None

        response = client.post(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/genres/",
            data={"genre_id": "2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"},
            headers=superuser_token_headers,
        )

        mock_add_movie_genre.assert_called_once_with(repository=mock_movie_repository, finder=mock_movie_finder)
        mock_add_movie_genre.return_value.execute.assert_called_once_with(
            params=AddMovieGenreParams(
                movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                genre_id=Id("2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"),
            )
        )

        assert response.status_code == 200

    def test_returns_400_and_calls_add_movie_genre_when_genre_already_assigned(
        self,
        client: TestClient,
        mock_add_movie_genre: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_add_movie_genre.return_value.execute.side_effect = GenreAlreadyAssigned

        response = client.post(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/genres/",
            data={"genre_id": "2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"},
            headers=superuser_token_headers,
        )

        mock_add_movie_genre.assert_called_once_with(repository=mock_movie_repository, finder=mock_movie_finder)
        mock_add_movie_genre.return_value.execute.assert_called_once_with(
            params=AddMovieGenreParams(
                movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                genre_id=Id("2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"),
            )
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "The genre is already assigned to the movie"}


class TestRemoveMovieGenreEndpoint:
    @pytest.fixture
    def mock_remove_movie_genre(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.RemoveMovieGenre") as mock:
            yield mock

    @pytest.fixture
    def mock_movie_repository(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_movie_finder(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, session: Session, client: TestClient, superuser_token_headers: dict[str, str]) -> None:
        genre_model = SqlModelGenreFactoryTest(session=session).create(name="Action")
        movie_model = SqlModelMovieBuilderTest(session=session).with_genre(genre_model=genre_model).build()

        response = client.delete(
            f"api/v1/movies/{movie_model.id}/genres/{genre_model.id}/",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        assert len(movie_model.genres) == 0

    def test_returns_200_and_calls_remove_movie_genre(
        self,
        client: TestClient,
        mock_remove_movie_genre: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_remove_movie_genre.return_value.execute.return_value = None

        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/genres/2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e/",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200

        mock_remove_movie_genre.assert_called_once_with(repository=mock_movie_repository, finder=mock_movie_finder)
        mock_remove_movie_genre.return_value.execute.assert_called_once_with(
            movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            genre_id=Id("2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"),
        )

        assert response.status_code == 200

    def test_returns_400_and_calls_remove_movie_genre_when_genre_not_assigned(
        self,
        client: TestClient,
        mock_remove_movie_genre: Mock,
        mock_movie_repository: Mock,
        mock_movie_finder: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_remove_movie_genre.return_value.execute.side_effect = GenreNotAssigned

        response = client.delete(
            "api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/genres/2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e/",
            headers=superuser_token_headers,
        )

        mock_remove_movie_genre.assert_called_once_with(repository=mock_movie_repository, finder=mock_movie_finder)
        mock_remove_movie_genre.return_value.execute.assert_called_once_with(
            movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            genre_id=Id("2e9c5b5b-1b7e-4b7e-8d8b-2b4b4b1f1a4e"),
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "The genre is not assigned to the movie"}


class TestGetMovieEndpoint:
    @pytest.fixture
    def mock_find_movie(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.FindMovie") as mock:
            yield mock

    @pytest.fixture
    def mock_movie_finder(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, session: Session, client: TestClient) -> None:
        movie_model = (
            SqlModelMovieBuilderTest(session=session)
            .with_id(UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_genre(
                SqlModelGenreFactoryTest(session=session).create(
                    id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"), name="Action"
                )
            )
            .with_showtime(
                id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
            .build()
        )

        response = client.get(f"api/v1/movies/{movie_model.id}/?showtime_date=2023-04-03")

        assert response.status_code == 200
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "title": "Deadpool & Wolverine",
            "description": "Deadpool and a variant of Wolverine.",
            "poster_image": "deadpool_and_wolverine.jpg",
            "genres": [
                {
                    "id": "d108f84b-3568-446b-896c-3ba2bc74cda9",
                    "name": "Action",
                },
            ],
            "showtimes": [
                {
                    "id": "d7c10c00-9598-4618-956a-ff3aa82dd33f",
                    "show_datetime": "2023-04-03T22:00:00Z",
                },
            ],
        }

    def test_returns_200_and_calls_find_movie(
        self, client: TestClient, mock_find_movie: Mock, mock_movie_finder: Mock
    ) -> None:
        mock_find_movie.return_value.execute.return_value = (
            MovieBuilder()
            .with_id(id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_genre(
                genre=GenreFactoryTest().create(
                    id=Id("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                    name="Action",
                )
            )
            .with_genre(
                genre=GenreFactoryTest().create(
                    id=Id("d108f84b-3568-446b-896c-3ba2bc74cda8"),
                    name="Comedy",
                )
            )
            .with_showtime(
                showtime=MovieShowtimeFactoryTest().create(
                    id=Id("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                    show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                )
            )
            .build()
        )

        response = client.get("api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/?showtime_date=2023-04-03")

        mock_find_movie.assert_called_once_with(finder=mock_movie_finder)
        mock_find_movie.return_value.execute.assert_called_once_with(
            params=FindMovieParams(
                movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                showtime_date=Date.from_datetime_date(date(2023, 4, 3)),
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
        self, client: TestClient, mock_find_movie: Mock, mock_movie_finder: Mock
    ) -> None:
        mock_find_movie.return_value.execute.side_effect = MovieDoesNotExist

        response = client.get("api/v1/movies/913822a0-750b-4cb6-b7b9-e01869d7d62d/?showtime_date=2023-04-03")

        mock_find_movie.assert_called_once_with(finder=mock_movie_finder)
        mock_find_movie.return_value.execute.assert_called_once_with(
            params=FindMovieParams(
                movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                showtime_date=Date.from_datetime_date(date(2023, 4, 3)),
            )
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "The movie does not exist"}


class TestListMoviesEndpoint:
    @pytest.fixture
    def mock_find_movies(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.FindMovies") as mock:
            yield mock

    @pytest.fixture
    def mock_movie_finder(self) -> Generator[Mock, None, None]:
        with patch("app.movies.infrastructure.api.endpoints.SqlModelMovieFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, session: Session, client: TestClient) -> None:
        action_genre = SqlModelGenreFactoryTest(session=session).create(
            id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"), name="Action"
        )
        comedy_genre = SqlModelGenreFactoryTest(session=session).create(name="Comedy")
        (
            SqlModelMovieBuilderTest(session=session)
            .with_id(UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_genre(genre_model=action_genre)
            .with_showtime(
                id=UUID("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
            .build()
        )
        SqlModelMovieBuilderTest(session=session).with_genre(genre_model=comedy_genre).with_showtime(
            show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
        ).build()
        SqlModelMovieBuilderTest(session=session).with_genre(genre_model=action_genre).with_showtime(
            show_datetime=datetime(2023, 4, 4, 22, 0, tzinfo=timezone.utc),
        ).build()

        response = client.get(f"api/v1/movies/?showtime_date=2023-04-03&genre_id={action_genre.id}")

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "title": "Deadpool & Wolverine",
                "description": "Deadpool and a variant of Wolverine.",
                "poster_image": "deadpool_and_wolverine.jpg",
                "genres": [
                    {
                        "id": "d108f84b-3568-446b-896c-3ba2bc74cda9",
                        "name": "Action",
                    },
                ],
                "showtimes": [
                    {
                        "id": "d7c10c00-9598-4618-956a-ff3aa82dd33f",
                        "show_datetime": "2023-04-03T22:00:00Z",
                    },
                ],
            }
        ]

    def test_returns_200_and_calls_find_movies(
        self, client: TestClient, mock_find_movies: Mock, mock_movie_finder: Mock
    ) -> None:
        mock_find_movies.return_value.execute.return_value = [
            MovieBuilder()
            .with_id(id=Id("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_title("Deadpool & Wolverine")
            .with_description("Deadpool and a variant of Wolverine.")
            .with_poster_image("deadpool_and_wolverine.jpg")
            .with_genre(genre=GenreFactoryTest().create(id=Id("d108f84b-3568-446b-896c-3ba2bc74cda8"), name="Comedy"))
            .with_showtime(
                showtime=MovieShowtimeFactoryTest().create(
                    id=Id("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                    show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                )
            )
            .build(),
            MovieBuilder()
            .with_id(id=Id("ec725625-f502-4d39-9401-a415d8c1f965"))
            .with_title("The Super Mario Bros. Movie")
            .with_description("An animated adaptation of the video game.")
            .with_poster_image("super_mario_bros.jpg")
            .with_genre(
                genre=GenreFactoryTest().create(id=Id("d108f84b-3568-446b-896c-3ba2bc74cda9"), name="Adventure")
            )
            .with_showtime(
                showtime=MovieShowtimeFactoryTest().create(
                    id=Id("d7c10c00-9598-4618-956a-ff3aa82dd44f"),
                    show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 23)),
                )
            )
            .build(),
        ]

        response = client.get("api/v1/movies/?showtime_date=2023-04-03")

        mock_find_movies.assert_called_once_with(finder=mock_movie_finder)
        mock_find_movies.return_value.execute.assert_called_once_with(
            params=FindMoviesParams(showtime_date=Date.from_datetime_date(date(2023, 4, 3)), genre_id=None)
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

    def test_returns_200_and_calls_find_movies_with_genre_filter(
        self, client: TestClient, mock_find_movies: Mock, mock_movie_finder: Mock
    ) -> None:
        mock_find_movies.return_value.execute.return_value = [
            MovieBuilder()
            .with_id(id=Id("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_genre(genre=GenreFactoryTest().create(id=Id("d108f84b-3568-446b-896c-3ba2bc74cda9"), name="Action"))
            .with_showtime(
                showtime=MovieShowtimeFactoryTest().create(
                    id=Id("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
                    show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22)),
                )
            )
            .build()
        ]

        response = client.get("api/v1/movies/?showtime_date=2023-04-03&genre_id=d108f84b-3568-446b-896c-3ba2bc74cda9")

        mock_find_movies.assert_called_once_with(finder=mock_movie_finder)
        mock_find_movies.return_value.execute.assert_called_once_with(
            params=FindMoviesParams(
                showtime_date=Date.from_datetime_date(date(2023, 4, 3)),
                genre_id=Id("d108f84b-3568-446b-896c-3ba2bc74cda9"),
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
        self, client: TestClient, mock_find_movies: Mock, mock_movie_finder: Mock
    ) -> None:
        mock_find_movies.return_value.execute.return_value = []

        response = client.get("api/v1/movies/?showtime_date=2023-04-03")

        mock_find_movies.assert_called_once_with(finder=mock_movie_finder)
        mock_find_movies.return_value.execute.assert_called_once_with(
            params=FindMoviesParams(showtime_date=Date.from_datetime_date(date(2023, 4, 3)), genre_id=None)
        )

        assert response.status_code == 200
        assert response.json() == []
