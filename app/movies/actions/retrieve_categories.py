from app.movies.domain.entities import Category
from app.movies.domain.repositories.category_repository import CategoryRepository


class RetrieveCategories:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Category]:
        return self._repository.get_all()
