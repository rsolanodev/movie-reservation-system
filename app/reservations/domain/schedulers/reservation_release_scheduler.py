from datetime import timedelta
from uuid import UUID


class ReservationReleaseScheduler:
    def schedule(self, reservation_id: UUID, delay: timedelta) -> None: ...
