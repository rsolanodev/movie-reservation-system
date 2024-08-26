from uuid import UUID

from sqlmodel import Session

from app.movies.infrastructure.models import GenreModel, MovieModel


class SqlModelMovieFactory:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._movie_model: MovieModel

    def create(self) -> "SqlModelMovieFactory":
        movie_model = MovieModel(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image="deadpool_and_wolverine.jpg",
        )
        self._session.add(movie_model)
        self._movie_model = movie_model
        return self

    def add_genre(self) -> "SqlModelMovieFactory":
        genre_model = GenreModel(
            id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"), name="Action"
        )
        self._movie_model.genres.append(genre_model)
        self._session.add(self._movie_model)
        return self

    def get(self) -> MovieModel:
        return self._movie_model
