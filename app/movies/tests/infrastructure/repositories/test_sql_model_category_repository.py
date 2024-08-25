from sqlmodel import Session

from app.movies.domain.entities import Category
from app.movies.infrastructure.models import CategoryModel
from app.movies.infrastructure.repositories.sql_model_category_repository import (
    SqlModelCategoryRepository,
)


class TestSqlModelCategoryRepository:
    def test_get_all_categories_ordered(self, session: Session) -> None:
        action_category = Category.create(name="Action")
        adventure_category = Category.create(name="Adventure")
        comedy_category = Category.create(name="Comedy")

        category_models: list[CategoryModel] = [
            CategoryModel.from_domain(action_category),
            CategoryModel.from_domain(adventure_category),
            CategoryModel.from_domain(comedy_category),
        ]
        session.add_all(category_models)
        session.commit()

        categories = SqlModelCategoryRepository(session=session).get_all()

        assert categories == [action_category, adventure_category, comedy_category]

    def test_get_all_categories_when_no_categories(self, session: Session) -> None:
        categories = SqlModelCategoryRepository(session=session).get_all()

        assert categories == []
