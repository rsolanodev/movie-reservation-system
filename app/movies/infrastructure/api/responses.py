from sqlmodel import SQLModel

from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.domain.movie_showtime import MovieShowtime


class GenreResponse(SQLModel):
    id: str
    name: str

    @classmethod
    def from_domain(cls, genre: Genre) -> "GenreResponse":
        return cls(id=genre.id.value, name=genre.name)

    @classmethod
    def from_domain_list(cls, genres: list[Genre]) -> list["GenreResponse"]:
        return [cls.from_domain(genre) for genre in genres]


class MovieShowtimeResponse(SQLModel):
    id: str
    show_datetime: str

    @classmethod
    def from_domain(cls, showtime: MovieShowtime) -> "MovieShowtimeResponse":
        return cls(id=showtime.id.value, show_datetime=showtime.show_datetime.to_string())

    @classmethod
    def from_domain_list(cls, showtimes: list[MovieShowtime]) -> list["MovieShowtimeResponse"]:
        return [cls.from_domain(showtime) for showtime in showtimes]


class MovieResponse(SQLModel):
    id: str
    title: str
    description: str | None
    poster_image: str | None

    @classmethod
    def from_domain(cls, movie: Movie) -> "MovieResponse":
        return cls(id=movie.id.value, title=movie.title, description=movie.description, poster_image=movie.poster_image)


class MovieExtendedResponse(MovieResponse):
    genres: list[GenreResponse]
    showtimes: list[MovieShowtimeResponse]

    @classmethod
    def from_domain(cls, movie: Movie) -> "MovieExtendedResponse":
        return cls(
            id=movie.id.value,
            title=movie.title,
            description=movie.description,
            poster_image=movie.poster_image,
            genres=GenreResponse.from_domain_list(genres=movie.genres),
            showtimes=MovieShowtimeResponse.from_domain_list(showtimes=movie.showtimes),
        )

    @classmethod
    def from_domain_list(cls, movies: list[Movie]) -> list["MovieExtendedResponse"]:
        return [cls.from_domain(movie) for movie in movies]
