from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.domain.constants.unset import UNSET
from app.movies.actions.add_movie_genre import AddMovieGenre
from app.movies.actions.create_movie import CreateMovie, CreateMovieParams
from app.movies.actions.delete_movie import DeleteMovie
from app.movies.actions.remove_movie_genre import RemoveMovieGenre
from app.movies.actions.retrieve_genres import RetrieveGenres
from app.movies.actions.update_movie import UpdateMovie, UpdateMovieParams
from app.movies.domain.entities import Genre, Movie
from app.movies.domain.exceptions import (
    GenreNotAssignedException,
    MovieDoesNotExistException,
)
from app.movies.infrastructure.api.responses import GenreResponse, MovieResponse
from app.movies.infrastructure.api.utils import build_poster_image
from app.movies.infrastructure.repositories.sql_model_genre_repository import (
    SqlModelGenreRepository,
)
from app.movies.infrastructure.repositories.sql_model_movie_repository import (
    SqlModelMovieRepository,
)

router = APIRouter()


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
) -> Movie:
    return CreateMovie(
        repository=SqlModelMovieRepository(session=session),
    ).execute(
        params=CreateMovieParams(
            title=title,
            description=description,
            poster_image=build_poster_image(uploaded_file=poster_image),  # type: ignore
        )
    )


@router.patch(
    "/{movie_id}/",
    response_model=MovieResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_movie(
    session: SessionDep,
    movie_id: UUID,
    title: str = Form(min_length=1, max_length=100, default=UNSET),
    description: str | None = Form(default=UNSET),
    poster_image: UploadFile | None = File(default=UNSET),
) -> Movie:
    try:
        movie = UpdateMovie(
            repository=SqlModelMovieRepository(session=session),
        ).execute(
            params=UpdateMovieParams(
                id=movie_id,
                title=title,
                description=description,
                poster_image=build_poster_image(uploaded_file=poster_image),
            )
        )
    except MovieDoesNotExistException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The movie does not exist"
        )
    return movie


@router.delete(
    "/{movie_id}/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_movie(session: SessionDep, movie_id: UUID) -> None:
    try:
        DeleteMovie(
            repository=SqlModelMovieRepository(session=session),
        ).execute(id=movie_id)
    except MovieDoesNotExistException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The movie does not exist"
        )


@router.get(
    "/genres/",
    response_model=list[GenreResponse],
    status_code=status.HTTP_200_OK,
)
def retrieve_genres(session: SessionDep) -> list[Genre]:
    return RetrieveGenres(repository=SqlModelGenreRepository(session=session)).execute()


@router.post(
    "/{movie_id}/genres/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def add_movie_genre(
    session: SessionDep, movie_id: UUID, genre_id: UUID = Form(...)
) -> None:
    AddMovieGenre(repository=SqlModelMovieRepository(session=session)).execute(
        movie_id=movie_id, genre_id=genre_id
    )


@router.delete(
    "/{movie_id}/genres/{genre_id}/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def remove_movie_genre(session: SessionDep, movie_id: UUID, genre_id: UUID) -> None:
    try:
        RemoveMovieGenre(repository=SqlModelMovieRepository(session=session)).execute(
            movie_id=movie_id, genre_id=genre_id
        )
    except GenreNotAssignedException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The genre is not assigned to the movie",
        )
