from dataclasses import dataclass
from uuid import UUID

from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.movie import Movie
from app.movies.domain.poster_image import PosterImage
from app.movies.domain.repositories.movie_repository import MovieRepository


@dataclass(frozen=True)
class UpdateMovieParams:
    id: UUID
    title: str | None
    description: str | None
    poster_image: PosterImage | None


class UpdateMovie:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, params: UpdateMovieParams) -> Movie:
        movie = self._get_or_raise_exception(id=params.id)
        movie.update(
            title=params.title,
            description=params.description,
            poster_image=self._get_poster_image_filename(params.poster_image),
        )
        self._repository.save(movie=movie)
        return movie

    def _get_or_raise_exception(self, id: UUID) -> Movie:
        movie = self._repository.get(id=id)
        if movie is None:
            raise MovieDoesNotExist()
        return movie

    def _get_poster_image_filename(self, poster_image: PosterImage | None) -> str | None:
        if isinstance(poster_image, PosterImage):
            return poster_image.filename
        return poster_image
