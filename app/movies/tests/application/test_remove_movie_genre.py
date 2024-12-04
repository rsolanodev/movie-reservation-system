from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.movies.application.remove_movie_genre import RemoveMovieGenre
from app.movies.domain.exceptions import GenreNotAssigned
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.tests.factories.genre_factory_test import GenreFactoryTest
from app.shared.domain.value_objects.id import ID
from app.shared.tests.domain.builders.movie_builder import MovieBuilder


class TestRemoveMovieGenre:
    @pytest.fixture
    def mock_movie_repository(self) -> Any:
        return create_autospec(spec=MovieRepository, instance=True, spec_set=True)

    def test_removes_genre_from_movie(self, mock_movie_repository: Mock) -> None:
        mock_movie_repository.get.return_value = (
            MovieBuilder()
            .with_id(id=ID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
            .with_genre(genre=GenreFactoryTest().create(id=ID("3b74494d-0a95-49b1-91ef-bb211f802961"), name="Action"))
            .build()
        )

        RemoveMovieGenre(repository=mock_movie_repository).execute(
            movie_id=ID("913822a0-750b-4cb6-b7b9-e01869d7d62d"), genre_id=ID("3b74494d-0a95-49b1-91ef-bb211f802961")
        )

        mock_movie_repository.get.assert_called_once_with(id=ID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
        mock_movie_repository.remove_genre.assert_called_once_with(
            movie_id=ID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            genre_id=ID("3b74494d-0a95-49b1-91ef-bb211f802961"),
        )

    def test_raise_exception_when_genre_is_not_assigned_in_movie(self, mock_movie_repository: Mock) -> None:
        mock_movie_repository.get.return_value = (
            MovieBuilder().with_id(id=ID("913822a0-750b-4cb6-b7b9-e01869d7d62d")).build()
        )

        with pytest.raises(GenreNotAssigned):
            RemoveMovieGenre(repository=mock_movie_repository).execute(
                movie_id=ID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                genre_id=ID("3b74494d-0a95-49b1-91ef-bb211f802961"),
            )

        mock_movie_repository.get.assert_called_once_with(id=ID("913822a0-750b-4cb6-b7b9-e01869d7d62d"))
        mock_movie_repository.remove_genre.assert_not_called()
