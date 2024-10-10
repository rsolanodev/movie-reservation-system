from sqlmodel import select

from app.core.infrastructure.repositories.sql_model_repository import SqlModelRepository
from app.movies.domain.genre import Genre
from app.movies.domain.repositories.genre_repository import GenreRepository
from app.movies.infrastructure.models import GenreModel


class SqlModelGenreRepository(GenreRepository, SqlModelRepository):
    def get_all(self) -> list[Genre]:
        statement = select(GenreModel).order_by(GenreModel.name)
        genre_models = self._session.exec(statement).all()
        return [genre_model.to_domain() for genre_model in genre_models]
