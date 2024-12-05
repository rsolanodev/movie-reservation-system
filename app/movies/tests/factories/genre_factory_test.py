import uuid

from app.movies.domain.genre import Genre
from app.shared.domain.value_objects.id import Id


class GenreFactoryTest:
    def create(self, name: str, id: Id | None = None) -> Genre:
        return Genre(id=id or Id.from_uuid(uuid.uuid4()), name=name)
