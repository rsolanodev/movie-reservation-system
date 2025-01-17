from typing import Protocol

from app.shared.domain.payment_intent import PaymentIntent


class PaymentClient(Protocol):
    def create_payment_intent(self, amount: float) -> PaymentIntent: ...
