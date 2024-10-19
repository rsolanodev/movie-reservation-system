from uuid import UUID


class ReservationRelease:
    def execute(self, reservation_id: UUID) -> None: ...
