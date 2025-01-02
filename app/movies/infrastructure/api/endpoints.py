from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.movies.application.add_movie_genre import AddMovieGenre
from app.movies.application.create_movie import CreateMovie, CreateMovieParams
from app.movies.application.delete_movie import DeleteMovie
from app.movies.application.remove_movie_genre import RemoveMovieGenre
from app.movies.application.retrieve_genres import RetrieveGenres
from app.movies.application.retrieve_movie import RetrieveMovie, RetrieveMovieParams
from app.movies.application.retrieve_movies import RetrieveMovies, RetrieveMoviesParams
from app.movies.application.update_movie import UpdateMovie, UpdateMovieParams
from app.movies.domain.exceptions import (
    GenreAlreadyAssigned,
    GenreNotAssigned,
    MovieDoesNotExist,
)
from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.infrastructure.api.responses import (
    CreateMovieResponse,
    GenreResponse,
    RetrieveMovieResponse,
    UpdateMovieResponse,
)
from app.movies.infrastructure.api.utils import build_poster_image
from app.movies.infrastructure.finders.sqlmodel_movie_finder import SqlModelMovieFinder
from app.movies.infrastructure.repositories.sqlmodel_genre_repository import (
    SqlModelGenreRepository,
)
from app.movies.infrastructure.repositories.sqlmodel_movie_repository import (
    SqlModelMovieRepository,
)
from app.shared.domain.value_objects.id import Id

router = APIRouter()


@router.get(
    "/genres/",
    response_model=list[GenreResponse],
    status_code=status.HTTP_200_OK,
)
def retrieve_genres(session: SessionDep) -> list[Genre]:
    return RetrieveGenres(repository=SqlModelGenreRepository(session=session)).execute()


@router.get(
    "/",
    response_model=list[RetrieveMovieResponse],
    status_code=status.HTTP_200_OK,
)
def retrieve_movies(
    session: SessionDep, showtime_date: str, genre_id: str | None = None
) -> list[RetrieveMovieResponse]:
    movies = RetrieveMovies(finder=SqlModelMovieFinder(session=session)).execute(
        params=RetrieveMoviesParams.from_primitives(showtime_date=showtime_date, genre_id=genre_id),
    )
    return [RetrieveMovieResponse.from_domain(movie=movie) for movie in movies]


@router.post(
    "/",
    response_model=CreateMovieResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_movie(
    session: SessionDep,
    title: str = Form(min_length=1, max_length=100),
    description: str | None = Form(default=None),
    poster_image: UploadFile | None = File(default=None),
) -> Movie:
    return CreateMovie(
        repository=SqlModelMovieRepository(session=session),
    ).execute(
        params=CreateMovieParams(
            title=title,
            description=description,
            poster_image=build_poster_image(uploaded_file=poster_image),
        )
    )


@router.get(
    "/{movie_id}/",
    response_model=RetrieveMovieResponse,
    status_code=status.HTTP_200_OK,
)
def retrieve_movie(session: SessionDep, movie_id: str, showtime_date: str) -> RetrieveMovieResponse:
    try:
        movie = RetrieveMovie(finder=SqlModelMovieFinder(session=session)).execute(
            params=RetrieveMovieParams.from_primitives(movie_id=movie_id, showtime_date=showtime_date)
        )
    except MovieDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The movie does not exist")
    return RetrieveMovieResponse.from_domain(movie=movie)


@router.patch(
    "/{movie_id}/",
    response_model=UpdateMovieResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_movie(
    session: SessionDep,
    movie_id: str,
    title: str = Form(min_length=1, max_length=100, default=None),
    description: str | None = Form(default=None),
    poster_image: UploadFile | None = None,
) -> UpdateMovieResponse:
    try:
        movie = UpdateMovie(
            repository=SqlModelMovieRepository(session=session),
            finder=SqlModelMovieFinder(session=session),
        ).execute(
            params=UpdateMovieParams(
                id=Id(movie_id),
                title=title,
                description=description,
                poster_image=build_poster_image(uploaded_file=poster_image),
            )
        )
    except MovieDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The movie does not exist")
    return UpdateMovieResponse.from_domain(movie=movie)


@router.delete(
    "/{movie_id}/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_movie(session: SessionDep, movie_id: str) -> None:
    try:
        DeleteMovie(
            repository=SqlModelMovieRepository(session=session),
            finder=SqlModelMovieFinder(session=session),
        ).execute(id=Id(movie_id))
    except MovieDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The movie does not exist")


@router.post(
    "/{movie_id}/genres/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def add_movie_genre(session: SessionDep, movie_id: str, genre_id: str = Form(...)) -> None:
    try:
        AddMovieGenre(
            repository=SqlModelMovieRepository(session=session),
            finder=SqlModelMovieFinder(session=session),
        ).execute(movie_id=Id(movie_id), genre_id=Id(genre_id))
    except GenreAlreadyAssigned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The genre is already assigned to the movie",
        )


@router.delete(
    "/{movie_id}/genres/{genre_id}/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def remove_movie_genre(session: SessionDep, movie_id: str, genre_id: str) -> None:
    try:
        RemoveMovieGenre(
            repository=SqlModelMovieRepository(session=session),
            finder=SqlModelMovieFinder(session=session),
        ).execute(movie_id=Id(movie_id), genre_id=Id(genre_id))
    except GenreNotAssigned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The genre is not assigned to the movie",
        )
