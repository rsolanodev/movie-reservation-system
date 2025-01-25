from app.payments.application.commands.refund_payment import RefundPayment, RefundPaymentParams
from app.reservations.domain.events import ReservationCancelled
from app.shared.domain.events.event_subscriber import EventSubscriber
from app.shared.infrastructure.clients.stripe_client import StripeClient


class RefundWhenReservationCancelled(EventSubscriber[ReservationCancelled]):
    action: str = "refund"

    def on(self, event: ReservationCancelled) -> None:
        if event.provider_payment_id is None:
            return

        RefundPayment(payment_client=StripeClient()).execute(
            RefundPaymentParams(reservation_id=event.reservation_id, provider_payment_id=event.provider_payment_id)
        )
