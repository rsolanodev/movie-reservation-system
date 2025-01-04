from dataclasses import dataclass
from typing import BinaryIO


@dataclass
class PosterImage:
    filename: str
    file: BinaryIO
