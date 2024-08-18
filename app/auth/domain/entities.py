from dataclasses import dataclass
from enum import StrEnum


class TokenType(StrEnum):
    BEARER = "bearer"


@dataclass
class Token:
    access_token: str
    token_type: TokenType
    expires_in: int
