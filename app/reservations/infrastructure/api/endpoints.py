from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.reservations.application.create_reservation import CreateReservation, CreateReservationParams
from app.reservations.domain.exceptions import SeatsNotAvailable
from app.reservations.infrastructure.api.payloads import CreateReservationPayload
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.reservations.infrastructure.schedulers.celery_reservation_release_scheduler import (
    CeleryReservationReleaseScheduler,
)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_reservation(session: SessionDep, request_body: CreateReservationPayload, current_user: CurrentUser) -> None:
    try:
        CreateReservation(
            repository=SqlModelReservationRepository(session=session),
            reservation_release_scheduler=CeleryReservationReleaseScheduler(),
        ).execute(
            params=CreateReservationParams(
                showtime_id=request_body.showtime_id,
                seat_ids=request_body.seat_ids,
                user_id=current_user.id,
            )
        )
    except SeatsNotAvailable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seats not available")
