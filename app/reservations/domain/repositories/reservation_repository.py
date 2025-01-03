from typing import Protocol

from app.reservations.domain.movie_show_reservation import MovieShowReservation
from app.reservations.domain.reservation import Reservation
from app.shared.domain.value_objects.id import Id


class ReservationRepository(Protocol):
    def create(self, reservation: Reservation) -> None: ...
    def release(self, reservation_id: Id) -> None: ...
    def find_by_user_id(self, user_id: Id) -> list[MovieShowReservation]: ...
