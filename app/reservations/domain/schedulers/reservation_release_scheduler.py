from datetime import timedelta

from app.reservations.domain.value_objects.id import ID


class ReservationReleaseScheduler:
    def schedule(self, reservation_id: ID, delay: timedelta) -> None: ...
