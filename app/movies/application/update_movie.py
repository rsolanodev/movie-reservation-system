from dataclasses import dataclass

from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.finders.movie_finder import MovieFinder
from app.movies.domain.movie import Movie
from app.movies.domain.poster_image import PosterImage
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.domain.value_objects.id import Id


@dataclass(frozen=True)
class UpdateMovieParams:
    id: Id
    title: str | None
    description: str | None
    poster_image: PosterImage | None


class UpdateMovie:
    def __init__(self, repository: MovieRepository, finder: MovieFinder) -> None:
        self._repository = repository
        self._finder = finder

    def execute(self, params: UpdateMovieParams) -> Movie:
        movie = self._get_or_raise_exception(id=params.id)
        movie.update(
            title=params.title,
            description=params.description,
            poster_image=self._get_poster_image_filename(params.poster_image),
        )
        self._repository.save(movie=movie)
        return movie

    def _get_or_raise_exception(self, id: Id) -> Movie:
        movie = self._finder.find_movie(movie_id=id)
        if movie is None:
            raise MovieDoesNotExist()
        return movie

    def _get_poster_image_filename(self, poster_image: PosterImage | None) -> str | None:
        if isinstance(poster_image, PosterImage):
            return poster_image.filename
        return poster_image
