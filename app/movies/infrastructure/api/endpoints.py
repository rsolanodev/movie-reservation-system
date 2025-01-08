from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.movies.application.commands.add_movie_genre import AddMovieGenre, AddMovieGenreParams
from app.movies.application.commands.create_movie import CreateMovie, CreateMovieParams
from app.movies.application.commands.delete_movie import DeleteMovie
from app.movies.application.commands.remove_movie_genre import RemoveMovieGenre
from app.movies.application.commands.update_movie import UpdateMovie, UpdateMovieParams
from app.movies.application.queries.find_all_genres import FindAllGenres
from app.movies.application.queries.find_movie import FindMovie, FindMovieParams
from app.movies.application.queries.find_movies import FindMovies, FindMoviesParams
from app.movies.domain.exceptions import (
    GenreAlreadyAssigned,
    GenreNotAssigned,
    MovieDoesNotExist,
)
from app.movies.infrastructure.api.responses import GenreResponse, MovieExtendedResponse, MovieResponse
from app.movies.infrastructure.finders.sqlmodel_genre_finder import SqlModelGenreFinder
from app.movies.infrastructure.finders.sqlmodel_movie_finder import SqlModelMovieFinder
from app.movies.infrastructure.repositories.sqlmodel_movie_repository import SqlModelMovieRepository
from app.shared.domain.value_objects.id import Id
from app.shared.infrastructure.storages.s3_storage import PublicMediaS3Storage

router = APIRouter()


@router.get("/genres/", response_model=list[GenreResponse], status_code=status.HTTP_200_OK)
def list_genres(session: SessionDep) -> list[GenreResponse]:
    genres = FindAllGenres(finder=SqlModelGenreFinder(session=session)).execute()
    return GenreResponse.from_domain_list(genres=genres)


@router.get("/", response_model=list[MovieExtendedResponse], status_code=status.HTTP_200_OK)
def list_movies(session: SessionDep, showtime_date: str, genre_id: str | None = None) -> list[MovieExtendedResponse]:
    movies = FindMovies(finder=SqlModelMovieFinder(session=session)).execute(
        params=FindMoviesParams.from_primitives(showtime_date=showtime_date, genre_id=genre_id),
    )
    return MovieExtendedResponse.from_domain_list(movies=movies)


@router.post(
    "/",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_movie(
    session: SessionDep,
    title: str = Form(min_length=1, max_length=100),
    description: str | None = Form(default=None),
    poster_image: UploadFile | None = File(default=None),
) -> MovieResponse:
    movie = CreateMovie(repository=SqlModelMovieRepository(session=session), storage=PublicMediaS3Storage()).execute(
        params=CreateMovieParams.from_fastapi(title=title, description=description, upload_poster_image=poster_image)
    )
    return MovieResponse.from_domain(movie=movie)


@router.get("/{movie_id}/", response_model=MovieExtendedResponse, status_code=status.HTTP_200_OK)
def get_movie(session: SessionDep, movie_id: str, showtime_date: str) -> MovieExtendedResponse:
    try:
        movie = FindMovie(finder=SqlModelMovieFinder(session=session)).execute(
            params=FindMovieParams.from_primitives(movie_id=movie_id, showtime_date=showtime_date)
        )
    except MovieDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The movie does not exist")
    return MovieExtendedResponse.from_domain(movie=movie)


@router.patch(
    "/{movie_id}/",
    response_model=MovieResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_movie(
    session: SessionDep,
    movie_id: str,
    title: str = Form(min_length=1, max_length=100, default=None),
    description: str | None = Form(default=None),
    poster_image: UploadFile | None = None,
) -> MovieResponse:
    try:
        movie = UpdateMovie(
            repository=SqlModelMovieRepository(session=session),
            finder=SqlModelMovieFinder(session=session),
            storage=PublicMediaS3Storage(),
        ).execute(
            params=UpdateMovieParams.from_fastapi(
                id=movie_id, title=title, description=description, upload_poster_image=poster_image
            )
        )
    except MovieDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The movie does not exist")
    return MovieResponse.from_domain(movie=movie)


@router.delete("/{movie_id}/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_superuser)])
def delete_movie(session: SessionDep, movie_id: str) -> None:
    try:
        DeleteMovie(
            repository=SqlModelMovieRepository(session=session),
            finder=SqlModelMovieFinder(session=session),
        ).execute(id=Id(movie_id))
    except MovieDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The movie does not exist")


@router.post(
    "/{movie_id}/genres/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_superuser)]
)
def add_movie_genre(session: SessionDep, movie_id: str, genre_id: str = Form(...)) -> None:
    try:
        AddMovieGenre(
            repository=SqlModelMovieRepository(session=session), finder=SqlModelMovieFinder(session=session)
        ).execute(params=AddMovieGenreParams.from_primitives(movie_id=movie_id, genre_id=genre_id))
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
