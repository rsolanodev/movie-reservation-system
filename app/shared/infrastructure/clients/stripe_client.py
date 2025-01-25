import stripe
from stripe import SignatureVerificationError, StripeError

from app.payments.domain.exceptions import InvalidSignature
from app.settings import get_settings
from app.shared.domain.clients.payment_client import PaymentClient
from app.shared.domain.exceptions import RefundError
from app.shared.domain.payment_event import PaymentEvent
from app.shared.domain.payment_intent import PaymentIntent

settings = get_settings()


class StripeClient(PaymentClient):
    def __init__(self) -> None:
        self._provider = stripe
        self._provider.api_key = settings.STRIPE_API_KEY

    def create_payment_intent(self, amount: float) -> PaymentIntent:
        payment_intent = self._provider.PaymentIntent.create(
            amount=int(amount * 100),
            currency=settings.STRIPE_DEFAULT_CURRENCY,
            automatic_payment_methods={"enabled": True},
        )
        return PaymentIntent(
            client_secret=payment_intent.client_secret,  # type: ignore
            provider_payment_id=payment_intent.id,
            amount=amount,
        )

    def verify_payment(self, payload: bytes, signature: str) -> PaymentEvent:
        try:
            event = self._provider.Webhook.construct_event(  # type: ignore
                payload=payload, sig_header=signature, secret=settings.STRIPE_WEBHOOK_SECRET
            )
            return PaymentEvent(type=event.type, payment_intent_id=event.data.object["id"])
        except SignatureVerificationError:
            raise InvalidSignature()

    def refund_payment(self, payment_id: str) -> None:
        try:
            self._provider.Refund.create(payment_intent=payment_id)
        except StripeError:
            raise RefundError()
