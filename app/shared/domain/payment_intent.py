from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentIntent:
    client_secret: str | None
    provider_payment_id: str
    amount: float
