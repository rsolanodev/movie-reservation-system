from app.reservations.domain.events import ReservationCancelled
from app.shared.domain.events.event_subscriber import EventSubscriber


class RefundWhenReservationCancelled(EventSubscriber[ReservationCancelled]):
    action: str = "refund"

    def on(self, event: ReservationCancelled) -> None: ...
