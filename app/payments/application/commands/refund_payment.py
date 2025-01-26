import logging
from dataclasses import dataclass

from app.payments.domain.repositories.reservation_repository import ReservationRepository
from app.payments.domain.reservation import Reservation
from app.shared.domain.clients.payment_client import PaymentClient
from app.shared.domain.exceptions import RefundError
from app.shared.domain.value_objects.reservation_status import ReservationStatus

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RefundPaymentParams:
    reservation_id: str
    provider_payment_id: str


class RefundPayment:
    def __init__(self, payment_client: PaymentClient, reservation_repository: ReservationRepository) -> None:
        self._payment_client = payment_client
        self._reservation_repository = reservation_repository

    def execute(self, params: RefundPaymentParams) -> None:
        try:
            self._payment_client.refund_payment(payment_id=params.provider_payment_id)
            logger.info(
                "Refunding payment for reservation succeeded",
                extra={"reservation_id": params.reservation_id, "payment_id": params.provider_payment_id},
            )
        except RefundError:
            logger.error(
                "Refunding payment for reservation failed",
                extra={"reservation_id": params.reservation_id, "payment_id": params.provider_payment_id},
            )
            return

        self._reservation_repository.update(
            reservation=Reservation.update_status(id=params.reservation_id, status=ReservationStatus.REFUNDED)
        )
