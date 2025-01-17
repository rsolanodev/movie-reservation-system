from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentIntent:
    client_secret: str
    provider_payment_id: str
    amount: float
