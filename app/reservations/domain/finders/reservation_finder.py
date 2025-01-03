from typing import Protocol

from app.reservations.domain.movie_show_reservation import MovieShowReservation
from app.reservations.domain.reservation import Reservation
from app.shared.domain.value_objects.id import Id


class ReservationFinder(Protocol):
    def find_reservation(self, reservation_id: Id) -> Reservation: ...
    def find_movie_show_reservations_by_user_id(self, user_id: Id) -> list[MovieShowReservation]: ...
