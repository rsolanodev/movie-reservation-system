import uuid

from app.movies.domain.entities import Movie


class MovieFactory:
    def create(
        self,
        poster_image: str | None = "deadpool_and_wolverine.jpg",
    ) -> Movie:
        return Movie(
            id=uuid.UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image=poster_image,
        )
