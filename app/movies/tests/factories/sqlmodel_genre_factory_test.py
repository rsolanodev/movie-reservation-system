import uuid
from uuid import UUID

from sqlmodel import Session

from app.movies.infrastructure.models import GenreModel


class SqlModelGenreFactoryTest:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, name: str, id: UUID | None = None) -> GenreModel:
        genre_model = GenreModel(id=id or uuid.uuid4(), name=name)
        self._session.add(genre_model)
        return genre_model
