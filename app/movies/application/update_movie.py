from dataclasses import dataclass
from uuid import UUID

from app.core.domain.constants.unset import UnsetType
from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.movie import Movie
from app.movies.domain.poster_image import PosterImage
from app.movies.domain.repositories.movie_repository import MovieRepository


@dataclass
class UpdateMovieParams:
    id: UUID
    title: str | UnsetType
    description: str | None | UnsetType
    poster_image: PosterImage | None | UnsetType


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

    def _get_poster_image_filename(self, poster_image: PosterImage | None | UnsetType) -> str | None | UnsetType:
        if isinstance(poster_image, PosterImage):
            return poster_image.filename
        return poster_image
