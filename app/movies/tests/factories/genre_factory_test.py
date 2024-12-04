import uuid

from app.movies.domain.genre import Genre
from app.shared.domain.value_objects.id import ID


class GenreFactoryTest:
    def create(self, name: str, id: ID | None = None) -> Genre:
        return Genre(id=id or ID.from_uuid(uuid.uuid4()), name=name)
