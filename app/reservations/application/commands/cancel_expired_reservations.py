from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.settings import get_settings
from app.shared.domain.value_objects.date_time import DateTime

settings = get_settings()


class CancelExpiredReservations:
    def __init__(self, repository: ReservationRepository, finder: ReservationFinder) -> None:
        self._repository = repository
        self._finder = finder

    def execute(self) -> None:
        reservations = self._finder.find_pending()

        expiration_datetime = DateTime.now().subtract_minutes(minutes=settings.RESERVATION_EXPIRATION_MINUTES)
        expired_reservations = reservations.expired(expiration_datetime=expiration_datetime)

        if expired_reservations:
            self._repository.cancel_reservations(reservation_ids=expired_reservations.ids)
