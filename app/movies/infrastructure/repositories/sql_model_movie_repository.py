from collections.abc import Sequence
from datetime import date, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import selectinload
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

    def get_available_movies_for_date(self, available_date: date) -> list[Movie]:
        movie_showtime_models: Sequence[tuple[MovieModel, ShowtimeModel]] = (
            self._session.exec(
                select(MovieModel, ShowtimeModel)
                .options(selectinload(MovieModel.genres))  # type: ignore
                .join(ShowtimeModel)
                .where(
                    func.date(ShowtimeModel.show_datetime) == available_date,
                    MovieModel.id == ShowtimeModel.movie_id,
                )
                .order_by(MovieModel.title, ShowtimeModel.show_datetime)  # type: ignore
            ).all()
        )

        movies: dict[UUID, Movie] = {}
        for movie_model, showtime_model in movie_showtime_models:
            if movie_model.id not in movies:
                movie = movie_model.to_domain()

                for genre_model in movie_model.genres:
                    movie.add_genre(genre_model.to_domain())
                movies[movie_model.id] = movie

            movie_showtime = self._build_movie_showtime(showtime_model)
            movies[movie_model.id].add_showtime(movie_showtime)

        return list(movies.values())

    def get_movie_for_date(self, movie_id: UUID, showtime_date: date) -> Movie | None:
        movie_showtime_models: Sequence[tuple[MovieModel, ShowtimeModel]] = (
            self._session.exec(
                select(MovieModel, ShowtimeModel)
                .options(selectinload(MovieModel.genres))  # type: ignore
                .join(ShowtimeModel)
                .where(
                    func.date(ShowtimeModel.show_datetime) == showtime_date,
                    MovieModel.id == movie_id,
                )
                .order_by(ShowtimeModel.show_datetime)  # type: ignore
            ).all()
        )

        if not movie_showtime_models:
            return None

        movie_model = movie_showtime_models[0][0]
        movie = movie_model.to_domain()

        for genre_model in movie_model.genres:
            movie.add_genre(genre_model.to_domain())

        for _, showtime_model in movie_showtime_models:
            movie_showtime = self._build_movie_showtime(showtime_model)
            movie.add_showtime(movie_showtime)

        return movie

    @staticmethod
    def _build_movie_showtime(showtime_model: ShowtimeModel) -> MovieShowtime:
        show_datetime = showtime_model.show_datetime

        if show_datetime.tzinfo is None:
            show_datetime = show_datetime.replace(tzinfo=timezone.utc)

        return MovieShowtime(
            id=showtime_model.id,
            show_datetime=show_datetime,
        )
