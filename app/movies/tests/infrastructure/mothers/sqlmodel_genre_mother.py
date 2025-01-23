from typing import Self
from uuid import UUID

from sqlmodel import Session

from app.movies.infrastructure.models import GenreModel


class SqlModelGenreMother:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._genre_model = GenreModel(id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"), name="Action")

    def with_id(self, id: UUID) -> Self:
        self._genre_model.id = id
        return self

    def with_name(self, name: str) -> Self:
        self._genre_model.name = name
        return self

    def create(self) -> GenreModel:
        self._session.add(self._genre_model)
        return self._genre_model
