from app.celery import app
from app.database import get_db_session
from app.reservations.application.release_reservation import ReleaseReservation
from app.reservations.infrastructure.finders.sqlmodel_reservation_finder import SqlModelReservationFinder
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.shared.domain.value_objects.id import Id


@app.task
def release_reservation_task(reservation_id: str) -> None:
    with get_db_session() as session:
        ReleaseReservation(
            repository=SqlModelReservationRepository(session=session),
            finder=SqlModelReservationFinder(session=session),
        ).execute(reservation_id=Id(reservation_id))
