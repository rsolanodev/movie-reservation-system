from sqlmodel import SQLModel

from app.auth.domain.token import Token


class TokenResponse(SQLModel):
    access_token: str
    token_type: str
    expires_in: int

    @classmethod
    def from_domain(cls, token: Token) -> "TokenResponse":
        return cls(access_token=token.access_token, token_type=token.token_type, expires_in=token.expires_in)
