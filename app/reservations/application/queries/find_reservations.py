from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.movie_show_reservation import MovieShowReservation
from app.shared.domain.value_objects.id import Id


class FindReservations:
    def __init__(self, finder: ReservationFinder) -> None:
        self._finder = finder

    def execute(self, user_id: Id) -> list[MovieShowReservation]:
        return self._finder.find_movie_show_reservations_by_user_id(user_id=user_id)
