from dataclasses import dataclass

from app.payments.domain.exceptions import ReservationNotFound
from app.payments.domain.finders.reservation_finder import ReservationFinder
from app.payments.domain.repositories.reservation_repository import ReservationRepository
from app.shared.domain.clients.payment_client import PaymentClient


@dataclass(frozen=True)
class ConfirmPaymentParams:
    signature: str
    payload: bytes


class ConfirmPayment:
    def __init__(
        self,
        reservation_finder: ReservationFinder,
        reservation_repository: ReservationRepository,
        payment_client: PaymentClient,
    ):
        self._reservation_finder = reservation_finder
        self._reservation_repository = reservation_repository
        self._payment_client = payment_client

    def execute(self, params: ConfirmPaymentParams) -> None:
        payment_event = self._payment_client.verify_payment(payload=params.payload, signature=params.signature)

        if not payment_event.was_successful():
            return

        reservation = self._reservation_finder.find_by_payment_id(provider_payment_id=payment_event.payment_intent_id)

        if not reservation:
            raise ReservationNotFound()

        reservation.confirm()
        self._reservation_repository.update(reservation=reservation)
