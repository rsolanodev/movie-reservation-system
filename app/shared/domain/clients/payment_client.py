from typing import Protocol


class PaymentClient(Protocol):
    def create_checkout_session(self) -> str: ...
