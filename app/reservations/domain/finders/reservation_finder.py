from typing import Protocol

from app.reservations.domain.reservation import Reservation
from app.shared.domain.value_objects.id import Id


class ReservationFinder(Protocol):
    def find_reservation(self, reservation_id: Id) -> Reservation: ...
