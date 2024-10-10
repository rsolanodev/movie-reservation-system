from sqlmodel import SQLModel

from app.auth.domain.token import TokenType


class TokenResponse(SQLModel):
    access_token: str
    token_type: TokenType
    expires_in: int
