from dataclasses import dataclass


@dataclass(frozen=True)
class ConfirmPaymentParams:
    signature: str
    payload: bytes


class ConfirmPayment:
    def execute(self, params: ConfirmPaymentParams) -> None: ...
