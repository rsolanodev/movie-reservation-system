from dataclasses import dataclass


@dataclass
class PosterImage:
    filename: str | None
    content: bytes
    content_type: str | None
