from fastapi import APIRouter, File, Form, UploadFile

from app.api.deps import SessionDep
from app.movies.actions.create_movie import CreateMovie, CreateMovieParams
from app.movies.infrastructure.api.schemas import MovieSchema
from app.movies.infrastructure.api.utils import build_poster_image
from app.movies.infrastructure.repositories.sql_model_movie_repository import (
    SqlModelMovieRepository,
)

router = APIRouter()


@router.post("/", response_model=MovieSchema, status_code=201)
def create_movie(
    session: SessionDep,
    title: str = Form(min_length=1, max_length=100),
    description: str | None = Form(None),
    poster_image: UploadFile | None = File(None),
) -> MovieSchema:
    movie = CreateMovie(
        repository=SqlModelMovieRepository(session=session),
    ).execute(
        params=CreateMovieParams(
            title=title,
            description=description,
            poster_image=build_poster_image(uploaded_file=poster_image),
        )
    )
    return MovieSchema.from_domain(movie)
