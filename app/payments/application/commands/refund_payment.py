import logging
from dataclasses import dataclass

from app.shared.domain.clients.payment_client import PaymentClient
from app.shared.domain.exceptions import RefundError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RefundPaymentParams:
    reservation_id: str
    provider_payment_id: str


class RefundPayment:
    def __init__(self, payment_client: PaymentClient):
        self._payment_client = payment_client

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
