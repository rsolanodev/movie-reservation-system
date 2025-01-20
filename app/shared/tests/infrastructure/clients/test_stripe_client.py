from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from stripe import SignatureVerificationError

from app.payments.domain.exceptions import InvalidSignature
from app.settings import Settings
from app.shared.domain.payment_event import PaymentEvent
from app.shared.domain.payment_intent import PaymentIntent
from app.shared.infrastructure.clients.stripe_client import StripeClient


class TestStripeClient:
    @pytest.fixture
    def mock_stripe(self) -> Generator[Mock, None, None]:
        with patch("app.shared.infrastructure.clients.stripe_client.stripe", autospec=True) as mock:
            yield mock

    @pytest.fixture(autouse=True)
    def override_settings(self) -> Generator[None, None, None]:
        with patch(
            "app.shared.infrastructure.clients.stripe_client.settings",
            Settings(
                STRIPE_API_KEY="test_api_key",
                STRIPE_DEFAULT_CURRENCY="eur",
                STRIPE_WEBHOOK_SECRET="test_webhook_secret",
            ),
        ):
            yield

    def test_creates_payment_intent(self, mock_stripe: Mock) -> None:
        mock_stripe.PaymentIntent.create.return_value = Mock(
            client_secret="test_client_secret", id="test_provider_payment_id"
        )

        payment_intent = StripeClient().create_payment_intent(amount=10.0)

        mock_stripe.PaymentIntent.create.assert_called_once_with(
            amount=1000, currency="eur", automatic_payment_methods={"enabled": True}
        )

        assert payment_intent == PaymentIntent(
            client_secret="test_client_secret", provider_payment_id="test_provider_payment_id", amount=10.0
        )

    def test_verifies_payment(self, mock_stripe: Mock) -> None:
        mock_stripe.Webhook.construct_event.return_value = Mock(
            type="payment_intent.succeeded", data=Mock(object={"id": "test_provider_payment_id"})
        )

        payload = b'{"type": "payment_intent.succeeded"}'
        signature = "test_signature"

        payment_event = StripeClient().verify_payment(payload=payload, signature=signature)

        mock_stripe.Webhook.construct_event.assert_called_once_with(payload, signature, "test_webhook_secret")

        assert payment_event == PaymentEvent(
            type="payment_intent.succeeded", payment_intent_id="test_provider_payment_id"
        )

    def test_raises_invalid_signature_when_payment_verification_fails(self, mock_stripe: Mock) -> None:
        mock_stripe.Webhook.construct_event.side_effect = SignatureVerificationError(  # type: ignore
            "Invalid signature", "test_sig_header"
        )

        payload = b'{"type": "payment_intent.succeeded"}'
        signature = "invalid_signature"

        with pytest.raises(InvalidSignature):
            StripeClient().verify_payment(payload=payload, signature=signature)

        mock_stripe.Webhook.construct_event.assert_called_once_with(payload, signature, "test_webhook_secret")
