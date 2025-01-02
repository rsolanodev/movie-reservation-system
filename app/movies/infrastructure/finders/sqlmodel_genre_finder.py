from sqlmodel import select

from app.movies.domain.finders.genre_finder import GenreFinder
from app.movies.domain.genre import Genre
from app.movies.infrastructure.models import GenreModel
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository


class SqlModelGenreFinder(GenreFinder, SqlModelRepository):
    def find_all(self) -> list[Genre]:
        statement = select(GenreModel).order_by(GenreModel.name)
        genre_models = self._session.exec(statement).all()
        return [genre_model.to_domain() for genre_model in genre_models]
