import uuid

from app.movies.domain.entities import Genre, Movie, MovieShowtime


class MovieBuilder:
    def __init__(self) -> None:
        self.id: uuid.UUID = uuid.uuid4()
        self.title: str = "Deadpool & Wolverine"
        self.description: str = "Deadpool and a variant of Wolverine."
        self.poster_image: str | None = "deadpool_and_wolverine.jpg"

        self.genres: list[Genre] = []
        self.showtimes: list[MovieShowtime] = []

    def with_id(self, id: uuid.UUID) -> "MovieBuilder":
        self.id = id
        return self

    def with_title(self, title: str) -> "MovieBuilder":
        self.title = title
        return self

    def with_description(self, description: str) -> "MovieBuilder":
        self.description = description
        return self

    def with_poster_image(self, poster_image: str) -> "MovieBuilder":
        self.poster_image = poster_image
        return self

    def without_poster_image(self) -> "MovieBuilder":
        self.poster_image = None
        return self

    def with_genre(self, genre: Genre) -> "MovieBuilder":
        self.genres.append(genre)
        return self

    def with_showtime(self, showtime: MovieShowtime) -> "MovieBuilder":
        self.showtimes.append(showtime)
        return self

    def build(self) -> Movie:
        movie = Movie(
            id=self.id,
            title=self.title,
            description=self.description,
            poster_image=self.poster_image,
        )

        for genre in self.genres:
            movie.add_genre(genre)

        for showtime in self.showtimes:
            movie.add_showtime(showtime)

        return movie
