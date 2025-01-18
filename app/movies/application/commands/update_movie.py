from dataclasses import dataclass

from fastapi import UploadFile

from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.finders.movie_finder import MovieFinder
from app.movies.domain.movie import Movie
from app.movies.domain.poster_image import PosterImage
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.domain.storages.storage import Storage
from app.shared.domain.value_objects.id import Id


@dataclass(frozen=True)
class UpdateMovieParams:
    id: Id
    title: str | None
    description: str | None
    poster_image: PosterImage | None

    @classmethod
    def from_fastapi(
        cls, id: str, title: str | None, description: str | None, upload_poster_image: UploadFile | None
    ) -> "UpdateMovieParams":
        poster_image: PosterImage | None = None

        if upload_poster_image and upload_poster_image.filename:
            poster_image = PosterImage(filename=upload_poster_image.filename, file=upload_poster_image.file)
        return cls(id=Id(id), title=title, description=description, poster_image=poster_image)


class UpdateMovie:
    def __init__(self, repository: MovieRepository, finder: MovieFinder, storage: Storage) -> None:
        self._repository = repository
        self._finder = finder
        self._storage = storage

    def execute(self, params: UpdateMovieParams) -> Movie:
        movie = self._get_or_raise_exception(id=params.id)
        movie.update(title=params.title, description=params.description)

        if params.poster_image:
            poster_image_path = self._upload_poster_image(params.poster_image)
            movie.update(poster_image=poster_image_path)

        self._repository.save(movie=movie)
        return movie

    def _get_or_raise_exception(self, id: Id) -> Movie:
        movie = self._finder.find_movie(movie_id=id)
        if movie is None:
            raise MovieDoesNotExist()
        return movie

    def _upload_poster_image(self, poster_image: PosterImage) -> str:
        return self._storage.upload_file(file=poster_image.file, name=poster_image.filename)
