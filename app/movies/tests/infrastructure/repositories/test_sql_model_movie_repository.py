from datetime import date, datetime, timezone
from unittest.mock import ANY
from uuid import UUID

from sqlmodel import Session

from app.movies.domain.entities import Genre, Movie, MovieShowtime
from app.movies.infrastructure.models import MovieModel
from app.movies.infrastructure.repositories.sql_model_movie_repository import (
    SqlModelMovieRepository,
)
from app.movies.tests.infrastructure.factories.genre_model_factory import (
    GenreModelFactory,
)
from app.shared.tests.domain.builders.movie_builder import MovieBuilder
from app.shared.tests.infrastructure.builders.movie_model_builder import (
    MovieModelBuilder,
)
from app.shared.tests.infrastructure.factories.showtime_model_factory import (
    ShowtimeModelFactory,
)


class TestSqlModelMovieRepository:
    def test_creates_movie(self, session: Session) -> None:
        movie = MovieBuilder().build()

        SqlModelMovieRepository(session=session).save(movie=movie)

        movie_model = session.get_one(MovieModel, movie.id)
        assert movie_model.title == "Deadpool & Wolverine"
        assert movie_model.description == "Deadpool and a variant of Wolverine."
        assert movie_model.poster_image == "deadpool_and_wolverine.jpg"

    def test_updates_movie(self, session: Session) -> None:
        movie_model = MovieModelBuilder(session=session).build()

        movie = movie_model.to_domain()
        movie.title = "The Super Mario Bros. Movie"
        movie.description = "An animated adaptation of the video game."
        movie.poster_image = "super_mario_bros.jpg"

        SqlModelMovieRepository(session=session).save(movie=movie)

        session.refresh(movie_model)
        assert movie_model.title == "The Super Mario Bros. Movie"
        assert movie_model.description == "An animated adaptation of the video game."
        assert movie_model.poster_image == "super_mario_bros.jpg"

    def test_get_movie(self, session: Session) -> None:
        genre_model_factory = GenreModelFactory(session=session)
        movie_model = (
            MovieModelBuilder(session=session)
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_genre(
                genre_model=genre_model_factory.create(
                    id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"),
                    name="Action",
                )
            )
            .with_genre(
                genre_model=genre_model_factory.create(
                    id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77b"),
                    name="Comedy",
                )
            )
            .build()
        )

        movie = SqlModelMovieRepository(session=session).get(id=movie_model.id)

        assert movie == Movie(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image="deadpool_and_wolverine.jpg",
            genres=[
                Genre(id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"), name="Action"),
                Genre(id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77b"), name="Comedy"),
            ],
        )

    def test_delete_movie(self, session: Session) -> None:
        movie_model = MovieModelBuilder(session=session).build()

        SqlModelMovieRepository(session=session).delete(id=movie_model.id)

        assert session.get(MovieModel, movie_model.id) is None

    def test_add_genre_to_movie(self, session: Session) -> None:
        genre_model = GenreModelFactory(session=session).create(
            id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"),
            name="Action",
        )
        movie_model = MovieModelBuilder(session=session).build()

        SqlModelMovieRepository(session=session).add_genre(
            movie_id=movie_model.id, genre_id=genre_model.id
        )

        session.refresh(movie_model)
        assert movie_model.genres[0].id == UUID("393210d5-80ce-4d03-b896-5d89f15aa77a")
        assert movie_model.genres[0].name == "Action"

    def test_remove_genre_from_movie(self, session: Session) -> None:
        movie_model = (
            MovieModelBuilder(session=session)
            .with_genre(
                genre_model=GenreModelFactory(session=session).create(
                    id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"),
                    name="Action",
                )
            )
            .build()
        )

        SqlModelMovieRepository(session=session).remove_genre(
            movie_id=movie_model.id,
            genre_id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"),
        )

        session.refresh(movie_model)
        assert movie_model.genres == []

    def test_get_all_movies_ordered_by_title(self, session: Session) -> None:
        genre_model_factory = GenreModelFactory(session=session)
        (
            MovieModelBuilder(session=session)
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"))
            .with_title("The Super Mario Bros. Movie")
            .with_description("An animated adaptation of the video game.")
            .with_poster_image("super_mario_bros.jpg")
            .with_genre(genre_model=genre_model_factory.create(name="Adventure"))
            .with_genre(genre_model=genre_model_factory.create(name="Comedy"))
            .build()
        )
        (
            MovieModelBuilder(session=session)
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_title("Deadpool & Wolverine")
            .with_description("Deadpool and a variant of Wolverine.")
            .with_poster_image("deadpool_and_wolverine.jpg")
            .with_genre(genre_model=genre_model_factory.create(name="Action"))
            .build()
        )
        movies = SqlModelMovieRepository(session=session).get_all()

        assert movies == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=[
                    Genre(id=ANY, name="Action"),
                ],
            ),
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f965"),
                title="The Super Mario Bros. Movie",
                description="An animated adaptation of the video game.",
                poster_image="super_mario_bros.jpg",
                genres=[
                    Genre(id=ANY, name="Adventure"),
                    Genre(id=ANY, name="Comedy"),
                ],
            ),
        ]

    def test_get_movie_showtimes_ordered_by_show_datetime(
        self, session: Session
    ) -> None:
        movie_model = (
            MovieModelBuilder(session=session)
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_showtime(
                showtime_model=ShowtimeModelFactory(session=session).create(
                    id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                    movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                    show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                )
            )
            .with_showtime(
                showtime_model=ShowtimeModelFactory(session=session).create(
                    id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                    movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                    show_datetime=datetime(2023, 4, 3, 20, 0, tzinfo=timezone.utc),
                )
            )
            .build()
        )
        repository = SqlModelMovieRepository(session=session)
        showtimes = repository.get_showtimes(movie_model.id)

        assert showtimes == [
            MovieShowtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2023, 4, 3, 20, 0, tzinfo=timezone.utc),
            ),
            MovieShowtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            ),
        ]

    def test_get_movie_showtimes_no_showtimes(self, session: Session) -> None:
        movie_model = MovieModelBuilder(session=session).build()

        repository = SqlModelMovieRepository(session=session)
        showtimes = repository.get_showtimes(movie_model.id)

        assert showtimes == []

    def test_get_available_movies_for_date(self, session: Session) -> None:
        MovieModelBuilder(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            showtime_model=ShowtimeModelFactory(session=session).create(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
        ).build()

        MovieModelBuilder(session=session).with_id(
            id=UUID("fc725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            showtime_model=ShowtimeModelFactory(session=session).create(
                id=UUID("dbdd7b54-c561-4cbb-a55f-15853c60e601"),
                movie_id=UUID("fc725625-f502-4d39-9401-a415d8c1f964"),
                show_datetime=datetime(2023, 4, 4, 22, 0, tzinfo=timezone.utc),
            )
        ).build()

        movies = SqlModelMovieRepository(session=session).get_available_movies_for_date(
            available_date=date(2023, 4, 3)
        )

        assert movies == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=[],
                showtimes=[
                    MovieShowtime(
                        id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                        show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                    ),
                ],
            ),
        ]

    def test_get_available_movies_for_date_with_showtimes_on_date(
        self, session: Session
    ) -> None:
        MovieModelBuilder(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            showtime_model=ShowtimeModelFactory(session=session).create(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
        ).build()

        MovieModelBuilder(session=session).with_id(
            id=UUID("fc725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            showtime_model=ShowtimeModelFactory(session=session).create(
                id=UUID("dbdd7b54-c561-4cbb-a55f-15853c60e601"),
                movie_id=UUID("fc725625-f502-4d39-9401-a415d8c1f964"),
                show_datetime=datetime(2023, 4, 4, 22, 0, tzinfo=timezone.utc),
            )
        ).build()

        movies = SqlModelMovieRepository(session=session).get_available_movies_for_date(
            available_date=date(2023, 4, 3)
        )

        assert movies == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=[],
                showtimes=[
                    MovieShowtime(
                        id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                        show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                    ),
                ],
            ),
        ]

    def test_get_available_movies_for_date_with_showtimes_ordered(
        self, session: Session
    ) -> None:
        MovieModelBuilder(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            showtime_model=ShowtimeModelFactory(session=session).create(
                id=UUID("ebdd7b54-c561-4cbb-a55f-15853c60e601"),
                movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
            )
        ).with_showtime(
            showtime_model=ShowtimeModelFactory(session=session).create(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
        ).build()

        movies = SqlModelMovieRepository(session=session).get_available_movies_for_date(
            available_date=date(2023, 4, 3)
        )

        assert movies == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=[],
                showtimes=[
                    MovieShowtime(
                        id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                        show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                    ),
                    MovieShowtime(
                        id=UUID("ebdd7b54-c561-4cbb-a55f-15853c60e601"),
                        show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
                    ),
                ],
            ),
        ]
