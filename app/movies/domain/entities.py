import uuid
from dataclasses import dataclass


@dataclass
class PosterImage:
    filename: str | None
    content: bytes
    content_type: str | None


@dataclass
class Movie:
    id: uuid.UUID
    title: str
    description: str | None
    poster_image: str | None

    @classmethod
    def create(
        cls, title: str, description: str | None, poster_image: str | None
    ) -> "Movie":
        return cls(
            id=uuid.uuid4(),
            title=title,
            description=description,
            poster_image=poster_image,
        )

    def update(
        self, title: str, description: str | None, poster_image: str | None
    ) -> None:
        self.title = title
        self.description = description
        self.poster_image = poster_image
