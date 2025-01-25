from typing import Protocol

from app.shared.domain.payment_event import PaymentEvent
from app.shared.domain.payment_intent import PaymentIntent


class PaymentClient(Protocol):
    def create_payment_intent(self, amount: float) -> PaymentIntent: ...
    def verify_payment(self, payload: bytes, signature: str) -> PaymentEvent: ...
    def refund_payment(self, payment_id: str) -> None: ...
