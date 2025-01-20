from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentEvent:
    type: str
    payment_intent_id: str

    def was_successful(self) -> bool:
        return self.type == "payment_intent.succeeded"
