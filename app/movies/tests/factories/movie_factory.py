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
            description=(
                "Deadpool is offered a place in the Marvel Cinematic Universe by the Time "
                "Variance Authority, but instead recruits a variant of Wolverine to save "
                "his universe from extinction."
            ),
            poster_image=poster_image,
        )
