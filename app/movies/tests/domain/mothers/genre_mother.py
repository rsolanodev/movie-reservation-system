from app.movies.domain.genre import Genre
from app.shared.domain.value_objects.id import Id


class GenreMother:
    def __init__(self) -> None:
        self._genre = Genre(id=Id("c8693e5a-ac9c-4560-9970-7ae4f22ddf0a"), name="Adventure")

    def with_id(self, id: Id) -> "GenreMother":
        self._genre.id = id
        return self

    def with_name(self, name: str) -> "GenreMother":
        self._genre.name = name
        return self

    def create(self) -> Genre:
        return self._genre
