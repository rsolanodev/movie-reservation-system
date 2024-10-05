from uuid import UUID

from sqlmodel import select

from app.core.infrastructure.repositories.sql_model_repository import SqlModelRepository
from app.movies.domain.entities import Movie, MovieShowtime
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.infrastructure.models import GenreModel, MovieModel
from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelMovieRepository(MovieRepository, SqlModelRepository):
    def save(self, movie: Movie) -> None:
        movie_model = MovieModel.from_domain(movie=movie)
        self._session.merge(movie_model)
        self._session.commit()

    def get(self, id: UUID) -> Movie | None:
        movie_model = self._session.get(MovieModel, id)

        if movie_model is None:
            return None

        movie = movie_model.to_domain()
        for genre in movie_model.genres:
            movie.add_genre(genre.to_domain())
        return movie

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

    def get_all(self) -> list[Movie]:
        statement = select(MovieModel).order_by(MovieModel.title)
        movie_models = self._session.exec(statement).all()

        movies: list[Movie] = []
        for movie_model in movie_models:
            movie = movie_model.to_domain()

            for genre_model in movie_model.genres:
                movie.add_genre(genre_model.to_domain())

            movies.append(movie)
        return movies

    def get_showtimes(self, movie_id: UUID) -> list[MovieShowtime]:
        statement = (
            select(ShowtimeModel)
            .where(ShowtimeModel.movie_id == movie_id)
            .order_by(ShowtimeModel.show_datetime)  # type: ignore
        )
        showtime_models = self._session.exec(statement).all()
        return [
            self._build_movie_showtime(showtime_model)
            for showtime_model in showtime_models
        ]

    def _build_movie_showtime(self, showtime_model: ShowtimeModel) -> MovieShowtime:
        return MovieShowtime(
            id=showtime_model.id,
            show_datetime=showtime_model.show_datetime,
        )
