from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.movies.domain.finders.movie_finder import MovieFinder
from app.movies.domain.movie import Movie
from app.movies.domain.movie_showtime import MovieShowtime
from app.movies.infrastructure.models import MovieModel
from app.shared.domain.value_objects.date import Date
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.infrastructure.finders.sqlmodel_finder import SqlModelFinder
from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelMovieFinder(MovieFinder, SqlModelFinder):
    def find_movie(self, movie_id: Id) -> Movie | None:
        movie_model = self._session.get(MovieModel, movie_id.to_uuid())

        if movie_model is None:
            return None

        movie = movie_model.to_domain()
        for genre in movie_model.genres:
            movie.add_genre(genre.to_domain())
        return movie

    def find_movie_by_showtime_date(self, movie_id: Id, showtime_date: Date) -> Movie | None:
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

    def find_movies_by_showtime_date(self, showtime_date: Date) -> list[Movie]:
        movie_showtime_models: Sequence[tuple[MovieModel, ShowtimeModel]] = self._session.exec(
            select(MovieModel, ShowtimeModel)
            .options(selectinload(MovieModel.genres))  # type: ignore
            .join(ShowtimeModel)
            .where(
                func.date(ShowtimeModel.show_datetime) == showtime_date.value,
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

    @staticmethod
    def _build_movie_showtime(showtime_model: ShowtimeModel) -> MovieShowtime:
        return MovieShowtime(
            id=Id.from_uuid(showtime_model.id),
            show_datetime=DateTime.from_datetime(showtime_model.show_datetime),
        )
