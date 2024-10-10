from uuid import UUID

from app.movies.domain.genre import Genre


class MovieGenres(list[Genre]):
    def has_genre(self, genre_id: UUID) -> bool:
        return any(genre.id == genre_id for genre in self)
