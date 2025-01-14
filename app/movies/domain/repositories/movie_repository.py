from typing import Protocol

from app.movies.domain.movie import Movie
from app.shared.domain.value_objects.id import Id


class MovieRepository(Protocol):
    def save(self, movie: Movie) -> None: ...

    def delete(self, id: Id) -> None: ...

    def add_genre(self, movie_id: Id, genre_id: Id) -> None: ...

    def remove_genre(self, movie_id: Id, genre_id: Id) -> None: ...
