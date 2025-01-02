from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.movies.application.retrieve_genres import RetrieveGenres
from app.movies.domain.finders.genre_finder import GenreFinder
from app.movies.domain.genre import Genre


class TestRetrieveGenres:
    @pytest.fixture
    def mock_genre_finder(self) -> Any:
        return create_autospec(spec=GenreFinder, instance=True, spec_set=True)

    def test_returns_all_genres(self, mock_genre_finder: Mock) -> None:
        expected_genres: list[Genre] = [
            Genre.create(name="Action"),
            Genre.create(name="Adventure"),
            Genre.create(name="Comedy"),
        ]
        mock_genre_finder.find_all.return_value = expected_genres

        genres = RetrieveGenres(finder=mock_genre_finder).execute()

        assert genres == expected_genres
