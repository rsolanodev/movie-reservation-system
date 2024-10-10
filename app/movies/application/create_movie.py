from dataclasses import dataclass

from app.movies.domain.movie import Movie
from app.movies.domain.poster_image import PosterImage
from app.movies.domain.repositories.movie_repository import MovieRepository


@dataclass
class CreateMovieParams:
    title: str
    description: str | None
    poster_image: PosterImage | None


class CreateMovie:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, params: CreateMovieParams) -> Movie:
        movie = Movie.create(
            title=params.title,
            description=params.description,
            poster_image=self._get_poster_image_filename(params.poster_image),
        )
        self._repository.save(movie=movie)
        return movie

    def _get_poster_image_filename(self, poster_image: PosterImage | None) -> str | None:
        return poster_image.filename if poster_image else None
