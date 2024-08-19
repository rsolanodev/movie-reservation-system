import uuid
from dataclasses import dataclass

from fastapi import UploadFile


@dataclass
class Movie:
    id: uuid.UUID
    title: str
    description: str | None
    poster_image: str | None

    @classmethod
    def create(
        cls, title: str, description: str | None, poster_image: UploadFile
    ) -> "Movie":
        return cls(
            id=uuid.uuid4(),
            title=title,
            description=description,
            poster_image=poster_image.filename,
        )
