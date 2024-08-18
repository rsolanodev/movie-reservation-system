from sqlmodel import SQLModel

from app.auth.domain.entities import Token, TokenType


class TokenSchema(SQLModel):
    access_token: str
    token_type: TokenType
    expires_in: int

    @classmethod
    def from_domain(cls, token: Token) -> "TokenSchema":
        return TokenSchema(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=token.expires_in,
        )
