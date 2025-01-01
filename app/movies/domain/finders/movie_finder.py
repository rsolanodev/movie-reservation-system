from typing import Protocol

from app.movies.domain.movie import Movie
from app.shared.domain.value_objects.date import Date
from app.shared.domain.value_objects.id import Id


class MovieFinder(Protocol):
    def find_movie(self, movie_id: Id) -> Movie | None: ...

    def find_movie_by_showtime_date(self, movie_id: Id, showtime_date: Date) -> Movie | None: ...

    def find_movies_by_showtime_date(self, showtime_date: Date) -> list[Movie]: ...
