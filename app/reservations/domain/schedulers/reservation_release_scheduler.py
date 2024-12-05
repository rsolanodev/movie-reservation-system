from datetime import timedelta

from app.shared.domain.value_objects.id import Id


class ReservationReleaseScheduler:
    def schedule(self, reservation_id: Id, delay: timedelta) -> None: ...
