from uuid import UUID

from app.movies.domain.entities import Genre


class GenreFactory:
    def create(self) -> Genre:
        return Genre(
            id=UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
            name="Action",
        )
