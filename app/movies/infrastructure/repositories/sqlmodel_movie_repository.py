from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.movies.domain.movie import Movie
from app.movies.domain.movie_showtime import MovieShowtime
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.infrastructure.models import GenreModel, MovieModel
from app.shared.domain.value_objects.date import Date
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository
from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelMovieRepository(MovieRepository, SqlModelRepository):
    def save(self, movie: Movie) -> None:
        movie_model = MovieModel.from_domain(movie=movie)
        self._session.merge(movie_model)
        self._session.commit()

    def get(self, id: Id) -> Movie | None:
        movie_model = self._session.get(MovieModel, id.to_uuid())

        if movie_model is None:
            return None

        movie = movie_model.to_domain()
        for genre in movie_model.genres:
            movie.add_genre(genre.to_domain())
        return movie

    def delete(self, id: Id) -> None:
        movie_model = self._session.get(MovieModel, id.to_uuid())
        self._session.delete(movie_model)
        self._session.commit()

    def add_genre(self, movie_id: Id, genre_id: Id) -> None:
        movie_model = self._session.get_one(MovieModel, movie_id.to_uuid())
        genre_model = self._session.get_one(GenreModel, genre_id.to_uuid())

        if genre_model not in movie_model.genres:
            movie_model.genres.append(genre_model)
            self._session.add(movie_model)
            self._session.commit()

    def remove_genre(self, movie_id: Id, genre_id: Id) -> None:
        movie_model = self._session.get_one(MovieModel, movie_id.to_uuid())
        genre_model = self._session.get_one(GenreModel, genre_id.to_uuid())

        if genre_model in movie_model.genres:
            movie_model.genres.remove(genre_model)
            self._session.add(movie_model)
            self._session.commit()

    def get_available_movies_for_date(self, available_date: date) -> list[Movie]:
        movie_showtime_models: Sequence[tuple[MovieModel, ShowtimeModel]] = self._session.exec(
            select(MovieModel, ShowtimeModel)
            .options(selectinload(MovieModel.genres))  # type: ignore
            .join(ShowtimeModel)
            .where(
                func.date(ShowtimeModel.show_datetime) == available_date,
                MovieModel.id == ShowtimeModel.movie_id,
            )
            .order_by(MovieModel.title, ShowtimeModel.show_datetime)  # type: ignore
        ).all()

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

    def get_movie_for_date(self, movie_id: Id, showtime_date: Date) -> Movie | None:
        movie_showtime_models: Sequence[tuple[MovieModel, ShowtimeModel]] = self._session.exec(
            select(MovieModel, ShowtimeModel)
            .options(selectinload(MovieModel.genres))  # type: ignore
            .join(ShowtimeModel)
            .where(
                func.date(ShowtimeModel.show_datetime) == showtime_date.value,
                MovieModel.id == movie_id.to_uuid(),
            )
            .order_by(ShowtimeModel.show_datetime)  # type: ignore
        ).all()

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
        return MovieShowtime(
            id=Id.from_uuid(showtime_model.id),
            show_datetime=DateTime.from_datetime(showtime_model.show_datetime),
        )
