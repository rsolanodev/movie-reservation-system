from dataclasses import dataclass

from fastapi import UploadFile

from app.movies.domain.movie import Movie
from app.movies.domain.poster_image import PosterImage
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.domain.storages.storage import Storage


@dataclass
class CreateMovieParams:
    title: str
    description: str | None
    poster_image: PosterImage | None

    @classmethod
    def from_fastapi(
        cls, title: str, description: str | None, upload_poster_image: UploadFile | None
    ) -> "CreateMovieParams":
        poster_image: PosterImage | None = None

        if upload_poster_image and upload_poster_image.filename:
            poster_image = PosterImage(filename=upload_poster_image.filename, file=upload_poster_image.file)
        return cls(title=title, description=description, poster_image=poster_image)


class CreateMovie:
    def __init__(self, repository: MovieRepository, storage: Storage) -> None:
        self._repository = repository
        self._storage = storage

    def execute(self, params: CreateMovieParams) -> Movie:
        movie = Movie.create(title=params.title, description=params.description)

        if params.poster_image:
            poster_image_path = self._upload_poster_image(params.poster_image)
            movie.update(poster_image=poster_image_path)

        self._repository.save(movie=movie)
        return movie

    def _upload_poster_image(self, poster_image: PosterImage) -> str:
        return self._storage.upload_file(file=poster_image.file, name=poster_image.filename)
