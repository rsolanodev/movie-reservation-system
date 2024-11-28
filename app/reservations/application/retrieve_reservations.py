from app.reservations.domain.movie_reservation import MovieReservation
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.shared.domain.value_objects.id import ID


class RetrieveReservations:
    def __init__(self, repository: ReservationRepository) -> None:
        self._repository = repository

    def execute(self, user_id: ID) -> list[MovieReservation]:
        return self._repository.find_by_user_id(user_id=user_id)
