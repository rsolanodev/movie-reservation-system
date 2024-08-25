from sqlmodel import select

from app.core.infrastructure.repositories.sql_model_repository import SqlModelRepository
from app.movies.domain.entities import Category
from app.movies.domain.repositories.category_repository import CategoryRepository
from app.movies.infrastructure.models import CategoryModel


class SqlModelCategoryRepository(CategoryRepository, SqlModelRepository):
    def get_all(self) -> list[Category]:
        statement = select(CategoryModel).order_by(CategoryModel.name)
        category_models = self._session.exec(statement).all()
        return [category_model.to_domain() for category_model in category_models]
