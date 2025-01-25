from dataclasses import dataclass

from app.reservations.domain.exceptions import ReservationNotFound
from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.shared.domain.events.event_bus import EventBus
from app.shared.domain.value_objects.id import Id


@dataclass(frozen=True)
class CancelReservationParams:
    reservation_id: Id
    user_id: Id


class CancelReservation:
    def __init__(self, finder: ReservationFinder, repository: ReservationRepository, event_bus: EventBus) -> None:
        self._finder = finder
        self._repository = repository
        self._event_bus = event_bus

    def execute(self, params: CancelReservationParams) -> None:
        cancellable_reservation = self._finder.find_cancellable_reservation(params.reservation_id)

        if not cancellable_reservation:
            raise ReservationNotFound()

        cancellable_reservation.cancel_by_owner(user_id=params.user_id)
        self._repository.release(reservation=cancellable_reservation.reservation)
        self._event_bus.publish(events=cancellable_reservation.collect_events())
