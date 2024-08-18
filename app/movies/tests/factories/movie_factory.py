import uuid

from app.movies.domain.entities import Movie


class MovieFactory:
    def create(self) -> Movie:
        return Movie(
            id=uuid.UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            title="The Shawshank Redemption",
            description=(
                "A Maine banker convicted of the murder of his wife and her lover in 1947 "
                "gradually forms a friendship over a quarter century with a hardened convict, "
                "while maintaining his innocence and trying to remain hopeful through simple compassion."
            ),
            poster_image="images/the_shawshank_redemption.png",
        )
