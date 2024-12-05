from app.movies.domain.genre import Genre
from app.shared.domain.value_objects.id import Id


class MovieGenres(list[Genre]):
    def has_genre(self, genre_id: Id) -> bool:
        return any(genre.id == genre_id for genre in self)
