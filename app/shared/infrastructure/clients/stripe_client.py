import stripe

from app.settings import get_settings
from app.shared.domain.clients.payment_client import PaymentClient
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
            client_secret=payment_intent.client_secret,
            provider_payment_id=payment_intent.id,
            amount=amount,
        )
