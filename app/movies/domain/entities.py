import uuid
from dataclasses import dataclass


@dataclass
class Movie:
    id: uuid.UUID
    title: str
    description: str | None
    poster_image: str | None
