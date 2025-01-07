from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.movies.application.queries.find_all_genres import FindAllGenres
from app.movies.domain.finders.genre_finder import GenreFinder
from app.movies.domain.genre import Genre


class TestFindAllGenres:
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

        genres = FindAllGenres(finder=mock_genre_finder).execute()

        assert genres == expected_genres
