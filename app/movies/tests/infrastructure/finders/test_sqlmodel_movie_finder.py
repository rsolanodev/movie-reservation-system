from datetime import date, datetime, timezone
from uuid import UUID

import pytest
from sqlmodel import Session

from app.movies.domain.collections.movie_genres import MovieGenres
from app.movies.domain.collections.movie_showtimes import MovieShowtimes
from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.domain.movie_showtime import MovieShowtime
from app.movies.infrastructure.finders.sqlmodel_movie_finder import SqlModelMovieFinder
from app.movies.tests.factories.sqlmodel_genre_factory_test import SqlModelGenreFactoryTest
from app.shared.domain.value_objects.date import Date
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.tests.builders.sqlmodel_movie_builder_test import SqlModelMovieBuilderTest


class TestSqlModelMovieFinder:
    @pytest.fixture
    def finder(self, session: Session) -> SqlModelMovieFinder:
        return SqlModelMovieFinder(session=session)

    def test_find_movie(self, session: Session, finder: SqlModelMovieFinder) -> None:
        genre_model_factory = SqlModelGenreFactoryTest(session=session)
        movie_model = (
            SqlModelMovieBuilderTest(session=session)
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

        movie = finder.find_movie(movie_id=Id.from_uuid(movie_model.id))

        assert movie == Movie(
            id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image="deadpool_and_wolverine.jpg",
            genres=MovieGenres(
                [
                    Genre(id=Id("393210d5-80ce-4d03-b896-5d89f15aa77a"), name="Action"),
                    Genre(id=Id("393210d5-80ce-4d03-b896-5d89f15aa77b"), name="Comedy"),
                ]
            ),
        )

    def test_find_movie_by_showtime_date(self, session: Session, finder: SqlModelMovieFinder) -> None:
        SqlModelMovieBuilderTest(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            id=UUID("ebdd7b54-c561-4cbb-a55f-15853c60e601"),
            show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
        ).with_showtime(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
        ).with_showtime(
            id=UUID("dbdd7b54-c561-4cbb-a55f-15853c60e601"),
            show_datetime=datetime(2023, 4, 4, 22, 0, tzinfo=timezone.utc),
        ).build()

        movie = finder.find_movie_by_showtime_date(
            movie_id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
            showtime_date=Date.from_datetime_date(date(2023, 4, 3)),
        )

        assert movie == Movie(
            id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image="deadpool_and_wolverine.jpg",
            genres=MovieGenres([]),
            showtimes=MovieShowtimes(
                [
                    MovieShowtime(
                        id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                        show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                    ),
                    MovieShowtime(
                        id=Id("ebdd7b54-c561-4cbb-a55f-15853c60e601"),
                        show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 23, 0)),
                    ),
                ]
            ),
        )

    def test_find_movie_by_showtime_date_when_does_not_exist(self, finder: SqlModelMovieFinder) -> None:
        movie = finder.find_movie_by_showtime_date(
            movie_id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
            showtime_date=Date.from_datetime_date(date(2023, 4, 3)),
        )

        assert movie is None

    def test_find_movies_by_showtime_date(self, session: Session, finder: SqlModelMovieFinder) -> None:
        SqlModelMovieBuilderTest(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
        ).build()

        SqlModelMovieBuilderTest(session=session).with_id(
            id=UUID("fc725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            id=UUID("dbdd7b54-c561-4cbb-a55f-15853c60e601"),
            show_datetime=datetime(2023, 4, 4, 22, 0, tzinfo=timezone.utc),
        ).build()

        movies = finder.find_movies_by_showtime_date(showtime_date=Date.from_datetime_date(date(2023, 4, 3)))

        assert movies == [
            Movie(
                id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=MovieGenres([]),
                showtimes=MovieShowtimes(
                    [
                        MovieShowtime(
                            id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                            show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                        ),
                    ],
                ),
            ),
        ]

    def test_find_movies_by_showtime_date_with_showtimes_on_date(
        self, session: Session, finder: SqlModelMovieFinder
    ) -> None:
        SqlModelMovieBuilderTest(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
        ).build()

        SqlModelMovieBuilderTest(session=session).with_id(
            id=UUID("fc725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            id=UUID("dbdd7b54-c561-4cbb-a55f-15853c60e601"),
            show_datetime=datetime(2023, 4, 4, 22, 0, tzinfo=timezone.utc),
        ).build()

        movies = finder.find_movies_by_showtime_date(showtime_date=Date.from_datetime_date(date(2023, 4, 3)))

        assert movies == [
            Movie(
                id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=MovieGenres([]),
                showtimes=MovieShowtimes(
                    [
                        MovieShowtime(
                            id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                            show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                        ),
                    ],
                ),
            ),
        ]

    def test_find_movies_by_showtime_date_with_showtimes_ordered(
        self, session: Session, finder: SqlModelMovieFinder
    ) -> None:
        SqlModelMovieBuilderTest(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            id=UUID("ebdd7b54-c561-4cbb-a55f-15853c60e601"),
            show_datetime=datetime(2023, 4, 3, 23, 0, tzinfo=timezone.utc),
        ).with_showtime(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
        ).build()

        movies = finder.find_movies_by_showtime_date(showtime_date=Date.from_datetime_date(date(2023, 4, 3)))

        assert movies == [
            Movie(
                id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=MovieGenres([]),
                showtimes=MovieShowtimes(
                    [
                        MovieShowtime(
                            id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                            show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                        ),
                        MovieShowtime(
                            id=Id("ebdd7b54-c561-4cbb-a55f-15853c60e601"),
                            show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 23, 0)),
                        ),
                    ],
                ),
            ),
        ]
