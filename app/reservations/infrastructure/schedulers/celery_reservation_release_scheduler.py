from datetime import timedelta

from app.reservations.domain.schedulers.reservation_release_scheduler import ReservationReleaseScheduler
from app.reservations.infrastructure.tasks import release_reservation_task
from app.shared.domain.value_objects.id import Id


class CeleryReservationReleaseScheduler(ReservationReleaseScheduler):
    def schedule(self, reservation_id: Id, delay: timedelta) -> None:
        release_reservation_task.apply_async(args=(reservation_id,), countdown=delay.total_seconds())
