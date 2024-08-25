from sqlmodel import Session

from app.movies.domain.entities import Genre
from app.movies.infrastructure.models import GenreModel
from app.movies.infrastructure.repositories.sql_model_genre_repository import (
    SqlModelGenreRepository,
)


class TestSqlModelGenreRepository:
    def test_get_all_genres_ordered(self, session: Session) -> None:
        action_genre = Genre.create(name="Action")
        adventure_genre = Genre.create(name="Adventure")
        comedy_genre = Genre.create(name="Comedy")

        genre_models: list[GenreModel] = [
            GenreModel.from_domain(action_genre),
            GenreModel.from_domain(adventure_genre),
            GenreModel.from_domain(comedy_genre),
        ]
        session.add_all(genre_models)

        genres = SqlModelGenreRepository(session=session).get_all()

        assert genres == [action_genre, adventure_genre, comedy_genre]

    def test_get_all_genres_when_no_genres(self, session: Session) -> None:
        genres = SqlModelGenreRepository(session=session).get_all()

        assert genres == []
