from sqlmodel import SQLModel

from app.auth.domain.entities import TokenType


class TokenResponse(SQLModel):
    access_token: str
    token_type: TokenType
    expires_in: int
