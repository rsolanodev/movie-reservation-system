from app.movies.domain.genre import Genre
from app.shared.domain.value_objects.id import ID


class MovieGenres(list[Genre]):
    def has_genre(self, genre_id: ID) -> bool:
        return any(genre.id == genre_id for genre in self)
