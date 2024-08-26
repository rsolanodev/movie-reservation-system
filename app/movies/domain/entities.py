import uuid
from dataclasses import dataclass, field

from app.core.domain.constants.unset import UnsetType


@dataclass
class PosterImage:
    filename: str | None
    content: bytes
    content_type: str | None


@dataclass
class Genre:
    id: uuid.UUID
    name: str

    @classmethod
    def create(cls, name: str) -> "Genre":
        return cls(id=uuid.uuid4(), name=name)


@dataclass
class Movie:
    id: uuid.UUID
    title: str
    description: str | None
    poster_image: str | None
    genres: list[Genre] = field(default_factory=list)

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
        self,
        title: str | UnsetType,
        description: str | None | UnsetType,
        poster_image: str | None | UnsetType,
    ) -> None:
        if not isinstance(title, UnsetType):
            self.title = title

        if not isinstance(description, UnsetType):
            self.description = description

        if not isinstance(poster_image, UnsetType):
            self.poster_image = poster_image

    def add_genre(self, genre: Genre) -> None:
        self.genres.append(genre)

    def has_genre(self, genre_id: uuid.UUID) -> bool:
        return any(genre.id == genre_id for genre in self.genres)
