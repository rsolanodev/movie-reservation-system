from uuid import UUID

from app.movies.domain.entities import Genre


class GenreFactory:
    def create(self) -> Genre:
        return Genre(
            id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            name="Action",
        )
