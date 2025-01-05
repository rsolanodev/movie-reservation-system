from dataclasses import dataclass
from typing import BinaryIO


@dataclass
class PosterImage:
    filename: str | None
    file: BinaryIO
