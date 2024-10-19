from datetime import timedelta
from uuid import UUID

from app.reservations.domain.schedulers.reservation_release_scheduler import ReservationReleaseScheduler
from app.reservations.infrastructure.tasks import reservation_release_task


class CeleryReservationReleaseScheduler(ReservationReleaseScheduler):
    def schedule(self, reservation_id: UUID, delay: timedelta) -> None:
        reservation_release_task.apply_async(args=(str(reservation_id),), countdown=delay.total_seconds())
