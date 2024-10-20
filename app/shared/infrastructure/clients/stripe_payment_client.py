from stripe import StripeClient

from app.settings import settings
from app.shared.domain.clients.payment_client import PaymentClient


class StripePaymentClient(PaymentClient):
    def __init__(self) -> None:
        self._client = StripeClient(api_key=settings.STRIPE_API_KEY)

    def create_checkout_session(self) -> str:
        return ""
