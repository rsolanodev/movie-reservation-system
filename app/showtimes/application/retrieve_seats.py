from uuid import UUID

from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository
from app.showtimes.domain.seat import Seat


class RetrieveSeats:
    def __init__(self, repository: ShowtimeRepository) -> None:
        self._repository = repository

    def execute(self, showtime_id: UUID) -> list[Seat]:
        return self._repository.retrive_seats(showtime_id=showtime_id)
