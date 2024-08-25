from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.movies.actions.retrieve_categories import RetrieveCategories
from app.movies.domain.entities import Category
from app.movies.domain.repositories.category_repository import CategoryRepository


class TestRetrieveCategories:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(CategoryRepository, instance=True)

    def test_returns_all_categories(self, mock_repository: Mock) -> None:
        expected_categories: list[Category] = [
            Category.create(name="Action"),
            Category.create(name="Adventure"),
            Category.create(name="Comedy"),
        ]
        mock_repository.get_all.return_value = expected_categories

        categories = RetrieveCategories(repository=mock_repository).execute()

        assert categories == expected_categories
