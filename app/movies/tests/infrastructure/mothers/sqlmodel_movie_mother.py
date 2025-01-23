from uuid import UUID

from sqlmodel import Session

from app.movies.infrastructure.models import MovieModel


class SqlModelMovieMother:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._movie_model = MovieModel(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image="deadpool_and_wolverine.jpg",
        )

    def create(self) -> MovieModel:
        self._session.add(self._movie_model)
        return self._movie_model
