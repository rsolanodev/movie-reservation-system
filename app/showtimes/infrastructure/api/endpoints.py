from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.showtimes.actions.create_showtime import CreateShowtime, CreateShowtimeParams
from app.showtimes.actions.delete_showtime import DeleteShowtime
from app.showtimes.domain.exceptions import ShowtimeAlreadyExistsException
from app.showtimes.infrastructure.api.payloads import CreateShowtimePayload
from app.showtimes.infrastructure.repositories.sql_model_showtime_repository import (
    SqlModelShowtimeRepository,
)

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_showtime(session: SessionDep, request_body: CreateShowtimePayload) -> None:
    try:
        CreateShowtime(
            repository=SqlModelShowtimeRepository(session=session),
        ).execute(
            params=CreateShowtimeParams(
                movie_id=request_body.movie_id,
                show_datetime=request_body.show_datetime,
            )
        )
    except ShowtimeAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Showtime for movie already exists",
        )


@router.delete(
    "/{showtime_id}/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_showtime(session: SessionDep, showtime_id: UUID) -> None:
    DeleteShowtime(
        repository=SqlModelShowtimeRepository(session=session),
    ).execute(showtime_id=showtime_id)
