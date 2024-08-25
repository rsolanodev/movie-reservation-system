from uuid import UUID

from app.core.infrastructure.repositories.sql_model_repository import SqlModelRepository
from app.movies.domain.entities import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.infrastructure.models import GenreModel, MovieModel


class SqlModelMovieRepository(MovieRepository, SqlModelRepository):
    def save(self, movie: Movie) -> None:
        movie_model = MovieModel.from_domain(movie=movie)
        self._session.merge(movie_model)
        self._session.commit()

    def get(self, id: UUID) -> Movie | None:
        movie_model = self._session.get(MovieModel, id)
        return movie_model.to_domain() if movie_model else None

    def delete(self, id: UUID) -> None:
        movie_model = self._session.get(MovieModel, id)
        self._session.delete(movie_model)
        self._session.commit()

    def add_genre(self, movie_id: UUID, genre_id: UUID) -> None:
        movie_model = self._session.get_one(MovieModel, movie_id)
        genre_model = self._session.get_one(GenreModel, genre_id)

        if genre_model not in movie_model.genres:
            movie_model.genres.append(genre_model)
            self._session.add(movie_model)
            self._session.commit()

    def remove_genre(self, movie_id: UUID, genre_id: UUID) -> None:
        movie_model = self._session.get_one(MovieModel, movie_id)
        genre_model = self._session.get_one(GenreModel, genre_id)

        if genre_model in movie_model.genres:
            movie_model.genres.remove(genre_model)
            self._session.add(movie_model)
            self._session.commit()
