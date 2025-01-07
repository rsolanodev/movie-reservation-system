from sqlmodel import SQLModel

from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.domain.movie_showtime import MovieShowtime


class GenreResponse(SQLModel):
    id: str
    name: str

    @classmethod
    def from_domain(cls, genre: Genre) -> "GenreResponse":
        return cls(id=genre.id, name=genre.name)

    @classmethod
    def from_domain_list(cls, genres: list[Genre]) -> list["GenreResponse"]:
        return [cls.from_domain(genre) for genre in genres]


class MovieResponse(SQLModel):
    id: str
    title: str
    description: str | None
    poster_image: str | None


class MovieShowtimeResponse(SQLModel):
    id: str
    show_datetime: str

    @classmethod
    def from_domain(cls, showtime: MovieShowtime) -> "MovieShowtimeResponse":
        return cls(id=showtime.id, show_datetime=showtime.show_datetime.to_string())


class CreateMovieResponse(MovieResponse): ...


class UpdateMovieResponse(MovieResponse):
    @classmethod
    def from_domain(cls, movie: Movie) -> "UpdateMovieResponse":
        return cls(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            poster_image=movie.poster_image,
        )


class RetrieveMovieResponse(MovieResponse):
    genres: list[GenreResponse]
    showtimes: list[MovieShowtimeResponse]

    @classmethod
    def from_domain(cls, movie: Movie) -> "RetrieveMovieResponse":
        return cls(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            poster_image=movie.poster_image,
            genres=[GenreResponse.from_domain(genre) for genre in movie.genres],
            showtimes=[MovieShowtimeResponse.from_domain(showtime) for showtime in movie.showtimes],
        )
