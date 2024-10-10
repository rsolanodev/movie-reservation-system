import uuid
from uuid import UUID

from app.movies.domain.genre import Genre


class GenreFactory:
    def create(self, name: str, id: UUID | None = None) -> Genre:
        return Genre(id=id or uuid.uuid4(), name=name)
