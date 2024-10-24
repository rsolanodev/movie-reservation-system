from uuid import UUID

from app.celery import app
from app.database import get_db_session
from app.reservations.application.reservation_release import ReservationRelease
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository


@app.task
def reservation_release_task(reservation_id: str) -> None:
    with get_db_session() as session:
        ReservationRelease(repository=SqlModelReservationRepository(session=session)).execute(
            reservation_id=UUID(reservation_id)
        )
