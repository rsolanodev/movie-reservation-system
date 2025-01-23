from sqlmodel import Session

from app.movies.domain.genre import Genre
from app.movies.infrastructure.finders.sqlmodel_genre_finder import SqlModelGenreFinder
from app.movies.infrastructure.models import GenreModel


class TestSqlModelGenreFinder:
    def test_find_all_genres_ordered(self, session: Session) -> None:
        action_genre = Genre.create(name="Action")
        adventure_genre = Genre.create(name="Adventure")
        comedy_genre = Genre.create(name="Comedy")

        genre_models: list[GenreModel] = [
            GenreModel.from_domain(action_genre),
            GenreModel.from_domain(adventure_genre),
            GenreModel.from_domain(comedy_genre),
        ]
        session.add_all(genre_models)

        genres = SqlModelGenreFinder(session).find_all()

        assert genres == [action_genre, adventure_genre, comedy_genre]

    def test_find_all_genres_when_no_genres(self, session: Session) -> None:
        genres = SqlModelGenreFinder(session).find_all()

        assert genres == []
