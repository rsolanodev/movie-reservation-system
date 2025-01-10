from app.database import get_session
from app.reservations.application.commands.cancel_expired_reservations import CancelExpiredReservations
from app.reservations.infrastructure.finders.sqlmodel_reservation_finder import SqlModelReservationFinder
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository


def cancel_expired_reservations_job() -> None:
    with get_session() as session:
        CancelExpiredReservations(
            repository=SqlModelReservationRepository(session), finder=SqlModelReservationFinder(session)
        ).execute()
