from app.celery import app
from app.reservations.application.reservation_release import ReservationRelease


@app.task
def reservation_release_task(reservation_id: str):
    ReservationRelease().execute(reservation_id=reservation_id)
