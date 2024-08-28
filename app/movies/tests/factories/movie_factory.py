import uuid

from app.movies.domain.entities import Genre, Movie


class MovieFactory:
    def create(self) -> Movie:
        return Movie(
            id=uuid.UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image="deadpool_and_wolverine.jpg",
        )

    def create_without_poster(self) -> Movie:
        return Movie(
            id=uuid.UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image=None,
        )

    def create_with_genre(self) -> Movie:
        return Movie(
            id=uuid.UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image="deadpool_and_wolverine.jpg",
            genres=[
                Genre(
                    id=uuid.UUID("d108f84b-3568-446b-896c-3ba2bc74cda9"),
                    name="Action",
                )
            ],
        )
