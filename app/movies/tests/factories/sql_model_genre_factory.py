from uuid import UUID

from sqlmodel import Session

from app.movies.infrastructure.models import GenreModel


class SqlModelGenreFactory:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._genre_model: GenreModel

    def create(self) -> "SqlModelGenreFactory":
        genre_model = GenreModel(
            id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"), name="Action"
        )
        self._session.add(genre_model)
        self._genre_model = genre_model
        return self

    def get(self) -> GenreModel:
        return self._genre_model
