from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.movies.actions.add_movie_genre import AddMovieGenre
from app.movies.domain.repositories.movie_repository import MovieRepository


class TestAddMovieGenre:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(MovieRepository, instance=True)

    def test_adds_genre_to_movie(self, mock_repository: Mock) -> None:
        AddMovieGenre(repository=mock_repository).execute(
            movie_id=UUID("8a74f835-2911-4ec4-ac4a-ed3c013569bb"),
            genre_id=UUID("3b74494d-0a95-49b1-91ef-bb211f802961"),
        )

        mock_repository.add_genre.assert_called_once_with(
            movie_id=UUID("8a74f835-2911-4ec4-ac4a-ed3c013569bb"),
            genre_id=UUID("3b74494d-0a95-49b1-91ef-bb211f802961"),
        )
