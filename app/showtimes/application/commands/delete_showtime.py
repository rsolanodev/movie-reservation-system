from app.shared.domain.value_objects.id import Id
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository


class DeleteShowtime:
    def __init__(self, repository: ShowtimeRepository) -> None:
        self._repository = repository

    def execute(self, showtime_id: Id) -> None:
        self._repository.delete(showtime_id=showtime_id)
