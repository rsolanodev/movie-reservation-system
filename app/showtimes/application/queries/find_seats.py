from app.shared.domain.value_objects.id import Id
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository
from app.showtimes.domain.seat import Seat


class FindSeats:
    def __init__(self, repository: ShowtimeRepository) -> None:
        self._repository = repository

    def execute(self, showtime_id: Id) -> list[Seat]:
        return self._repository.retrive_seats(showtime_id=showtime_id)
