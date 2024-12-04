from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.reservations.application.cancel_reservation import CancelReservation, CancelReservationParams
from app.reservations.application.create_reservation import CreateReservation, CreateReservationParams
from app.reservations.application.retrieve_reservations import RetrieveReservations
from app.reservations.domain.exceptions import (
    ReservationDoesNotBelongToUser,
    ReservationDoesNotExist,
    SeatsNotAvailable,
    ShowtimeHasStarted,
)
from app.reservations.infrastructure.api.payloads import CreateReservationPayload
from app.reservations.infrastructure.api.responses import MovieReservationResponse
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.reservations.infrastructure.schedulers.celery_reservation_release_scheduler import (
    CeleryReservationReleaseScheduler,
)
from app.shared.domain.value_objects.id import ID

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_reservation(session: SessionDep, request_body: CreateReservationPayload, current_user: CurrentUser) -> None:
    try:
        CreateReservation(
            repository=SqlModelReservationRepository(session=session),
            reservation_release_scheduler=CeleryReservationReleaseScheduler(),
        ).execute(
            params=CreateReservationParams(
                showtime_id=ID(request_body.showtime_id),
                seat_ids=[ID(seat_id) for seat_id in request_body.seat_ids],
                user_id=ID.from_uuid(current_user.id),
            )
        )
    except SeatsNotAvailable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seats not available")


@router.get("/", response_model=list[MovieReservationResponse], status_code=status.HTTP_200_OK)
def retrieve_reservations(session: SessionDep, current_user: CurrentUser) -> list[MovieReservationResponse]:
    movie_reservations = RetrieveReservations(
        repository=SqlModelReservationRepository(session=session),
    ).execute(user_id=ID.from_uuid(current_user.id))
    return [MovieReservationResponse.from_domain(reservation) for reservation in movie_reservations]


@router.delete("/{reservation_id}/", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(session: SessionDep, reservation_id: str, current_user: CurrentUser) -> None:
    try:
        CancelReservation(
            repository=SqlModelReservationRepository(session=session),
        ).execute(
            params=CancelReservationParams(
                reservation_id=ID(reservation_id),
                user_id=ID.from_uuid(current_user.id),
            )
        )
    except ReservationDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    except ReservationDoesNotBelongToUser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reservation does not belong to user")
    except ShowtimeHasStarted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Showtime has started")
