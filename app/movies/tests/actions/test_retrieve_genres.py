from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.movies.application.retrieve_genres import RetrieveGenres
from app.movies.domain.entities import Genre
from app.movies.domain.repositories.genre_repository import GenreRepository


class TestRetrieveGenres:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(GenreRepository, instance=True)

    def test_returns_all_genres(self, mock_repository: Mock) -> None:
        expected_genres: list[Genre] = [
            Genre.create(name="Action"),
            Genre.create(name="Adventure"),
            Genre.create(name="Comedy"),
        ]
        mock_repository.get_all.return_value = expected_genres

        genres = RetrieveGenres(repository=mock_repository).execute()

        assert genres == expected_genres
