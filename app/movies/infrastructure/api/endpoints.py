from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.domain.constants.unset import UNSET
from app.movies.actions.create_movie import CreateMovie, CreateMovieParams
from app.movies.actions.delete_movie import DeleteMovie
from app.movies.actions.retrieve_categories import RetrieveCategories
from app.movies.actions.update_movie import UpdateMovie, UpdateMovieParams
from app.movies.domain.exceptions import MovieDoesNotExistException
from app.movies.infrastructure.api.schemas import CategorySchema, MovieSchema
from app.movies.infrastructure.api.utils import build_poster_image
from app.movies.infrastructure.repositories.sql_model_category_repository import (
    SqlModelCategoryRepository,
)
from app.movies.infrastructure.repositories.sql_model_movie_repository import (
    SqlModelMovieRepository,
)

router = APIRouter()


@router.post(
    "/",
    response_model=MovieSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_movie(
    session: SessionDep,
    title: str = Form(min_length=1, max_length=100),
    description: str | None = Form(default=None),
    poster_image: UploadFile | None = File(default=None),
) -> MovieSchema:
    movie = CreateMovie(
        repository=SqlModelMovieRepository(session=session),
    ).execute(
        params=CreateMovieParams(
            title=title,
            description=description,
            poster_image=build_poster_image(uploaded_file=poster_image),  # type: ignore
        )
    )
    return MovieSchema.from_domain(movie)


@router.patch(
    "/{movie_id}/",
    response_model=MovieSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_movie(
    session: SessionDep,
    movie_id: UUID,
    title: str = Form(min_length=1, max_length=100, default=UNSET),
    description: str | None = Form(default=UNSET),
    poster_image: UploadFile | None = File(default=UNSET),
) -> MovieSchema:
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
    return MovieSchema.from_domain(movie)


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
    "/categories/",
    response_model=list[CategorySchema],
    status_code=status.HTTP_200_OK,
)
def retrieve_categories(session: SessionDep) -> list[CategorySchema]:
    categories = RetrieveCategories(
        repository=SqlModelCategoryRepository(session=session)
    ).execute()

    return [CategorySchema.from_domain(category) for category in categories]
