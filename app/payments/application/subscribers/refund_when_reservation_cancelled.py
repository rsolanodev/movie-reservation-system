from app.database import get_session
from app.payments.application.commands.refund_payment import RefundPayment, RefundPaymentParams
from app.payments.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.reservations.domain.events import ReservationCancelled
from app.shared.domain.events.event_subscriber import EventSubscriber
from app.shared.infrastructure.clients.stripe_client import StripeClient


class RefundWhenReservationCancelled(EventSubscriber[ReservationCancelled]):
    action: str = "refund"

    def on(self, event: ReservationCancelled) -> None:
        if event.provider_payment_id is None:
            return

        with get_session() as session:
            RefundPayment(
                payment_client=StripeClient(),
                reservation_repository=SqlModelReservationRepository(session),
            ).execute(
                params=RefundPaymentParams(
                    reservation_id=event.reservation_id,
                    provider_payment_id=event.provider_payment_id,
                )
            )
