from dataclasses import dataclass

from fastapi import UploadFile

from app.movies.domain.entities import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository


@dataclass
class CreateMovieParams:
    title: str
    description: str | None
    poster_image: UploadFile


class CreateMovie:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, params: CreateMovieParams) -> Movie:
        movie = Movie.create(
            title=params.title,
            description=params.description,
            poster_image=params.poster_image,
        )
        self._repository.save(movie=movie)
        return movie
