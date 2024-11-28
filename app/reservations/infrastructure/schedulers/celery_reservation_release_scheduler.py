from datetime import timedelta

from app.reservations.domain.schedulers.reservation_release_scheduler import ReservationReleaseScheduler
from app.reservations.infrastructure.tasks import reservation_release_task
from app.shared.domain.value_objects.id import ID


class CeleryReservationReleaseScheduler(ReservationReleaseScheduler):
    def schedule(self, reservation_id: ID, delay: timedelta) -> None:
        reservation_release_task.apply_async(args=(reservation_id,), countdown=delay.total_seconds())
