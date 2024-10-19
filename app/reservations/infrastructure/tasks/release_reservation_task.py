from uuid import UUID

from app.celery import app
from app.reservations.application.reservation_release import ReservationRelease


@app.task
def reservation_release_task(reservation_id: str) -> None:
    ReservationRelease().execute(reservation_id=UUID(reservation_id))
