from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.shared.domain.value_objects.id import Id
from app.showtimes.application.create_showtime import CreateShowtime, CreateShowtimeParams
from app.showtimes.application.delete_showtime import DeleteShowtime
from app.showtimes.application.queries.find_seats import FindSeats
from app.showtimes.domain.exceptions import ShowtimeAlreadyExists
from app.showtimes.infrastructure.api.payloads import CreateShowtimePayload
from app.showtimes.infrastructure.api.responses import SeatResponse
from app.showtimes.infrastructure.repositories.sqlmodel_showtime_repository import SqlModelShowtimeRepository

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_superuser)])
def create_showtime(session: SessionDep, request_body: CreateShowtimePayload) -> None:
    try:
        CreateShowtime(repository=SqlModelShowtimeRepository(session=session)).execute(
            params=CreateShowtimeParams.from_primitives(
                movie_id=request_body.movie_id,
                room_id=request_body.room_id,
                show_datetime=request_body.show_datetime,
            )
        )
    except ShowtimeAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Showtime for movie already exists",
        )


@router.delete("/{showtime_id}/", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_active_superuser)])
def delete_showtime(session: SessionDep, showtime_id: str) -> None:
    DeleteShowtime(repository=SqlModelShowtimeRepository(session=session)).execute(showtime_id=Id(showtime_id))


@router.get("/{showtime_id}/seats/", response_model=list[SeatResponse], status_code=status.HTTP_200_OK)
def list_seats(session: SessionDep, showtime_id: str) -> list[SeatResponse]:
    seats = FindSeats(repository=SqlModelShowtimeRepository(session=session)).execute(showtime_id=Id(showtime_id))
    return SeatResponse.from_domain_list(seats)
